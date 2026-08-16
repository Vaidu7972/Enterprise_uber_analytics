import re

import pandas as pd
from sqlalchemy import text

from utils.db_connection import get_engine


engine = get_engine()


def get_gold_schema() -> str:
    """
    Read the available tables and columns from the Gold schema.
    """

    schema_query = text(
        """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'gold'
        ORDER BY table_name, ordinal_position;
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            schema_query
        ).mappings().all()

    if not rows:
        raise RuntimeError(
            "No tables were found in the Gold schema."
        )

    tables = {}

    for row in rows:

        table_name = row["table_name"]
        column_name = row["column_name"]
        data_type = row["data_type"]

        if table_name not in tables:
            tables[table_name] = []

        tables[table_name].append(
            f"{column_name} ({data_type})"
        )

    schema_lines = []

    for table_name, columns in tables.items():

        schema_lines.append(
            f"\ngold.{table_name}"
        )

        for column in columns:
            schema_lines.append(
                f"  - {column}"
            )

    return "\n".join(schema_lines)


def validate_read_only_sql(query: str) -> str:
    """
    Make sure an AI-generated query is read-only.
    """

    query = query.strip()

    if query.endswith(";"):
        query = query[:-1].strip()

    if not query:
        raise ValueError(
            "SQL query is empty."
        )

    lower_query = query.lower()

    if not (
        lower_query.startswith("select")
        or lower_query.startswith("with")
    ):
        raise ValueError(
            "Only SELECT or WITH queries are allowed."
        )

    dangerous_pattern = (
        r"\b("
        r"insert|update|delete|drop|alter|"
        r"truncate|create|grant|revoke|merge|"
        r"copy|call|execute|vacuum|refresh|"
        r"nextval|setval"
        r")\b"
    )

    if re.search(
        dangerous_pattern,
        lower_query
    ):
        raise ValueError(
            "Unsafe SQL operation detected."
        )

    if ";" in query:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    if "--" in query or "/*" in query:
        raise ValueError(
            "SQL comments are not allowed."
        )

    forbidden_sources = [
        "bronze.",
        "silver.",
        "information_schema",
        "pg_catalog",
    ]

    for source in forbidden_sources:

        if source in lower_query:
            raise ValueError(
                f"Access to '{source}' is not allowed."
            )

    locking_patterns = [
        "for update",
        "for no key update",
        "for share",
        "for key share",
    ]

    for pattern in locking_patterns:

        if pattern in lower_query:
            raise ValueError(
                "Locking SELECT statements are not allowed."
            )

    if "gold." not in lower_query:
        raise ValueError(
            "Data Agent queries must use the Gold schema."
        )

    return query


def execute_read_only_query(
    query: str,
    max_rows: int = 200
) -> pd.DataFrame:
    """
    Validate and execute a read-only SQL query with statement timeout and row limits.
    """
    safe_query = validate_read_only_sql(query)

    # Enforce default LIMIT 200 if no LIMIT is specified in the query
    if "limit" not in safe_query.lower():
        safe_query = f"{safe_query} LIMIT {max_rows}"

    try:
        with engine.connect() as connection:
            connection.execute(text("SET LOCAL statement_timeout = '5000ms';"))
            df = pd.read_sql_query(
                text(safe_query),
                connection
            )
        return df.head(max_rows)
    except Exception as err:
        error_msg = str(err)
        # Sanitize sensitive database credentials/connection strings if present
        if "Password" in error_msg or "password" in error_msg:
            raise RuntimeError("Database execution error: Connection failure.")
        raise RuntimeError(f"Database query error: {error_msg}")