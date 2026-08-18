import json               
from google.genai import types            #google gemini python sdk(how gemini responds)

from agentic_ai.config.agent_config import GEMINI_MODEL   #no need to write again again model = gemini 
from agentic_ai.llm.gemini_client import safe_generate_content     #safe_generate_content means only read - select and with query
from agentic_ai.prompts.data_agent_prompt import (
    DATA_AGENT_SQL_PROMPT,   #instruction to gemini when sql generated
    DATA_RESULT_PROMPT,
)
from agentic_ai.schemas.sql_plan import SQLPlan
from agentic_ai.tools.sql_tool import (
    get_gold_schema,
    execute_read_only_query,
)


import re   #regular expression - to detect patterns
from agentic_ai.memory.conversation_memory import resolve_entity_in_question, update_session_memory


def generate_sql_plan(
    question: str,
    error_context: str = None,
    previous_sql: str = None
) -> SQLPlan:
    """
    Generate read-only SQL plan for PostgreSQL Gold warehouse query.
    Evaluates entity-aware pattern extraction first (driver_id, customer_id, location, comparison).
    """
    q_lower = question.lower()

    if not error_context:
        # 1. Entity Extraction: Specific Driver ID (e.g. D101, D052)
        driver_match = re.search(r'\b(d\d{2,5})\b', question, re.IGNORECASE)
        if driver_match:
            driver_id = driver_match.group(1).upper()
            return SQLPlan(
                can_answer=True,
                sql=f"SELECT driver_id, driver_name, driver_city, driver_rating, total_revenue, total_trips FROM gold.driver_performance_mart WHERE UPPER(driver_id) = '{driver_id}';",
                tables_used=["gold.driver_performance_mart"],
                explanation=f"Targeted query for driver ID {driver_id} from driver performance mart."
            )

        # 2. Entity Extraction: Specific Customer ID (e.g. C101)
        customer_match = re.search(r'\b(c\d{2,5})\b', question, re.IGNORECASE)
        if customer_match:
            cust_id = customer_match.group(1).upper()
            return SQLPlan(
                can_answer=True,
                sql=f"SELECT customer_id, customer_name, city, gender FROM gold.dim_customer WHERE UPPER(customer_id) = '{cust_id}';",
                tables_used=["gold.dim_customer"],
                explanation=f"Targeted query for customer ID {cust_id} from customer dimension."
            )

        # 3. Entity Extraction: Location / City Filters (e.g. Pune, Mumbai, Delhi)
        known_cities = ["pune", "mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata", "ahmedabad", "jaipur"]
        matched_city = next((city for city in known_cities if city in q_lower), None)
        if matched_city:
            city_caps = matched_city.upper()
            return SQLPlan(
                can_answer=True,
                sql=f"SELECT driver_id, driver_name, driver_city, driver_rating, total_revenue, total_trips FROM gold.driver_performance_mart WHERE UPPER(driver_city) LIKE '%{city_caps}%' ORDER BY total_revenue DESC LIMIT 10;",
                tables_used=["gold.driver_performance_mart"],
                explanation=f"Querying drivers located in {matched_city.title()} from driver performance mart."
            )

        # 4. Intent: Weekend vs Weekday Analytics
        if any(kw in q_lower for kw in ["weekend", "weekday", "compare"]):
            return SQLPlan(
                can_answer=True,
                sql="SELECT date_key, is_weekend, total_revenue, total_trips FROM gold.revenue_mart ORDER BY date_key DESC LIMIT 30;",
                tables_used=["gold.revenue_mart"],
                explanation="Querying weekend vs weekday revenue metrics."
            )

        # 5. Intent: Broad Top Drivers Leaderboard
        if any(kw in q_lower for kw in ["top", "rank", "leaderboard", "best"]):
            return SQLPlan(
                can_answer=True,
                sql="SELECT driver_name, driver_city, driver_rating, total_revenue, total_trips FROM gold.driver_performance_mart ORDER BY total_revenue DESC LIMIT 5;",
                tables_used=["gold.driver_performance_mart"],
                explanation="Querying top drivers by revenue from driver performance mart."
            )

        # 6. Intent: Trend / Daily Revenue
        if any(kw in q_lower for kw in ["trend", "daily", "over time"]):
            return SQLPlan(
                can_answer=True,
                sql="SELECT date_key, total_revenue, total_trips FROM gold.revenue_mart ORDER BY date_key ASC LIMIT 30;",
                tables_used=["gold.revenue_mart"],
                explanation="Querying daily revenue trend from revenue mart."
            )

        # 7. Intent: Executive Warehouse KPIs
        if any(kw in q_lower for kw in ["revenue", "total", "kpi", "executive", "fare", "trip", "trips"]):
            return SQLPlan(
                can_answer=True,
                sql="SELECT * FROM gold.kpi_summary;",
                tables_used=["gold.kpi_summary"],
                explanation="Querying executive KPI metrics."
            )

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
            if plan and plan.sql:
                return plan
        except Exception:
            pass

    return SQLPlan(           #fallback if query fails or incorrect structure o/p
        can_answer=True,
        sql="SELECT * FROM gold.kpi_summary;",
        tables_used=["gold.kpi_summary"],
        explanation="Fallback warehouse KPI summary query."
    )


def explain_query_result(
    question: str,
    sql: str,
    dataframe
) -> str:

    # Instant Deterministic Result Summary Formatting
    if len(dataframe) == 1:
        row = dataframe.iloc[0].to_dict()   #to get first row of df
        formatted_items = []
        for k, v in row.items():
            if isinstance(v, float):
                formatted_items.append(f"**{k.replace('_', ' ').title()}:** `${v:,.2f}`" if "revenue" in k or "fare" in k else f"**{k.replace('_', ' ').title()}:** `{v:,.2f}`")
            elif isinstance(v, int):
                formatted_items.append(f"**{k.replace('_', ' ').title()}:** `{v:,}`")
            else:
                formatted_items.append(f"**{k.replace('_', ' ').title()}:** `{v}`")
        return "### PostgreSQL Gold Warehouse Metrics\n\n" + "\n".join([f"• {item}" for item in formatted_items])

    summary_lines = [f"### PostgreSQL Gold Query Result ({len(dataframe)} Records Returned)\n"]
    for idx, row in dataframe.head(5).iterrows():
        row_str = " | ".join([f"**{k.replace('_', ' ').title()}:** `{v}`" for k, v in row.items() if k != "created_at"])
        summary_lines.append(f"**{idx+1}.** {row_str}")

    return "\n".join(summary_lines)


def answer_data_question(
    question: str,
    max_retries: int = 1,
    session_id: str = "default_session"
):
    question = resolve_entity_in_question(question, session_id=session_id)
    error_context = None
    previous_sql = None

    for attempt in range(max_retries + 1):
        plan = generate_sql_plan(
            question,
            error_context=error_context,    #error aware & retry / self correction
            previous_sql=previous_sql
        )

        if not plan.can_answer:
            return {
                "answer": "The available Gold warehouse schema does not contain enough information to answer this question.",
                "sql": None,
                "data": None,
                "tables_used": plan.tables_used,
            }

        if not plan.sql:
            return {
                "answer": "The Data Agent could not generate a valid SQL query.",
                "sql": None,
                "data": None,
                "tables_used": plan.tables_used,
            }

        try:
            dataframe = execute_read_only_query(plan.sql)
            
            if dataframe.empty:
                return {
                    "answer": "The query executed successfully, but no matching records were found in the Gold warehouse.",
                    "sql": plan.sql,
                    "data": [],
                    "tables_used": plan.tables_used,
                }

            answer = explain_query_result(question, plan.sql, dataframe)
            records = dataframe.to_dict(orient="records")     #df to records convert 

            return {                       #final successful ans return 
                "answer": answer,
                "sql": plan.sql,
                "data": records,
                "tables_used": plan.tables_used,
            }

        except Exception as err:           #error handling logic
            error_context = str(err)       #skips all fixed rules  actual schema display  
            previous_sql = plan.sql
            if attempt == max_retries:
                return {
                    "answer": f"Data Agent execution failed after retries: {error_context}",
                    "sql": plan.sql,
                    "data": None,
                    "tables_used": plan.tables_used,
                }