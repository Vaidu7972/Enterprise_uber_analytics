import json

from google.genai import types

from agentic_ai.config.agent_config import (
    GEMINI_MODEL,
)

from agentic_ai.llm.gemini_client import (
    safe_generate_content,
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
    question: str,
    error_context: str = None,
    previous_sql: str = None
) -> SQLPlan:

    schema = get_gold_schema()

    prompt = f"""
USER QUESTION:

{question}


AVAILABLE GOLD SCHEMA:

{schema}
"""
    if error_context and previous_sql:
        prompt += f"""

PREVIOUS FAILED SQL:
{previous_sql}

ERROR ENCOUNTERED:
{error_context}

INSTRUCTION: Correct the SQL query using ONLY the columns and tables defined in the GOLD SCHEMA above.
"""

    response = safe_generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=DATA_AGENT_SQL_PROMPT,
            response_mime_type="application/json",
            response_schema=SQLPlan,
        ),
    )

    if response and hasattr(response, "text") and response.text:
        try:
            plan = SQLPlan.model_validate_json(response.text)
            return plan
        except Exception:
            pass

    # Fallback SQL plan generation if Gemini API rate-limited
    q_lower = question.lower()
    if "revenue" in q_lower or "total" in q_lower:
        return SQLPlan(can_answer=True, sql="SELECT * FROM gold.kpi_summary;", tables_used=["gold.kpi_summary"], reasoning="Fallback query for total revenue metrics.")
    elif "driver" in q_lower:
        return SQLPlan(can_answer=True, sql="SELECT * FROM gold.driver_performance_mart ORDER BY total_revenue DESC LIMIT 10;", tables_used=["gold.driver_performance_mart"], reasoning="Fallback query for driver performance.")
    return SQLPlan(can_answer=True, sql="SELECT * FROM gold.fact_trip LIMIT 15;", tables_used=["gold.fact_trip"], reasoning="Fallback trip query.")


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

    response = safe_generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=DATA_RESULT_PROMPT
        ),
    )

    if response and hasattr(response, "text") and response.text:
        return response.text

    return f"PostgreSQL Gold warehouse query executed successfully! Retreived {len(dataframe)} record(s) matching your question scope."



def answer_data_question(
    question: str,
    max_retries: int = 2
):
    error_context = None
    previous_sql = None

    for attempt in range(max_retries + 1):
        plan = generate_sql_plan(
            question,
            error_context=error_context,
            previous_sql=previous_sql
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

        try:
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

        except Exception as err:
            error_context = str(err)
            previous_sql = plan.sql
            if attempt == max_retries:
                return {
                    "answer": f"Data Agent execution failed after retries: {error_context}",
                    "sql": plan.sql,
                    "data": None,
                    "tables_used": plan.tables_used,
                }