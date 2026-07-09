import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

customers = pd.read_sql("""
SELECT
customer_id,
customer_name,
city,
gender
FROM silver.customer_clean
""", engine)

customers["effective_date"] = pd.Timestamp.today().date()
customers["end_date"] = None
customers["is_current"] = True

customers.to_sql(
    "dim_customer",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Customer Dimension Loaded Successfully!")
print("Rows:", len(customers))