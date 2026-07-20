import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Loading Customer Dimension...")

customers = pd.read_sql(
    text("""
        SELECT DISTINCT
            customer_id,
            customer_name,
            city,
            gender
        FROM silver.customer_clean
        WHERE customer_id IS NOT NULL
    """),
    engine
)

customers = customers[
    [
        "customer_id",
        "customer_name",
        "city",
        "gender"
    ]
]

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.dim_customer RESTART IDENTITY CASCADE"))

customers.to_sql(
    "dim_customer",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Customer Dimension Loaded Successfully!")
print("Rows:", len(customers))