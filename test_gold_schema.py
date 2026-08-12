from agentic_ai.tools.sql_tool import (
    get_gold_schema,
)


schema = get_gold_schema()

print("\n--- GOLD SCHEMA ---")
print(schema)