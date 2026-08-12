import json

from google.genai import types

from agentic_ai.config.agent_config import (
    GEMINI_MODEL,
)

from agentic_ai.llm.gemini_client import (
    client,
)

from agentic_ai.prompts.data_agent_prompt import (
    DATA_AGENT_SQL_PROMPT,
    DATA_RESULT_PROMPT,
)

from agentic_ai.schemas.sql_plan import (
    SQLPlan,
)

from agentic_ai.tools.sql_tool import (
    get_gold_schema,
    execute_read_only_query,
)


def generate_sql_plan(
    question: str
) -> SQLPlan:

    schema = get_gold_schema()

    prompt = f"""
USER QUESTION:

{question}


AVAILABLE GOLD SCHEMA:

{schema}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=DATA_AGENT_SQL_PROMPT,
            response_mime_type="application/json",
            response_schema=SQLPlan,
        ),
    )

    plan = SQLPlan.model_validate_json(
        response.text
    )

    return plan


def explain_query_result(
    question: str,
    sql: str,
    dataframe
) -> str:

    result_records = dataframe.head(
        50
    ).to_dict(
        orient="records"
    )

    result_json = json.dumps(
        result_records,
        default=str,
        indent=2
    )

    prompt = f"""
USER QUESTION:

{question}


EXECUTED SQL:

{sql}


DATABASE RESULT:

{result_json}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=DATA_RESULT_PROMPT
        ),
    )

    return response.text


def answer_data_question(
    question: str
):

    plan = generate_sql_plan(
        question
    )

    if not plan.can_answer:

        return {
            "answer": (
                "The available Gold warehouse schema "
                "does not contain enough information "
                "to answer this question."
            ),
            "sql": None,
            "data": None,
            "tables_used": plan.tables_used,
        }

    if not plan.sql:

        return {
            "answer": (
                "The Data Agent could not generate "
                "a valid SQL query."
            ),
            "sql": None,
            "data": None,
            "tables_used": plan.tables_used,
        }

    dataframe = execute_read_only_query(
        plan.sql
    )

    if dataframe.empty:

        return {
            "answer": (
                "The query executed successfully, "
                "but no matching records were found."
            ),
            "sql": plan.sql,
            "data": dataframe,
            "tables_used": plan.tables_used,
        }

    answer = explain_query_result(
        question,
        plan.sql,
        dataframe
    )

    return {
        "answer": answer,
        "sql": plan.sql,
        "data": dataframe,
        "tables_used": plan.tables_used,
    }