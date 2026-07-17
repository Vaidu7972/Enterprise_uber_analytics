import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Clearing old gold.dim_driver data...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.dim_driver RESTART IDENTITY CASCADE"))

print("Reading silver.driver_clean...")

drivers = pd.read_sql(
    text("""
        SELECT DISTINCT
            driver_id,
            driver_name,
            city,
            rating
        FROM silver.driver_clean
        WHERE driver_id IS NOT NULL
    """),
    engine
)

drivers["effective_date"] = pd.Timestamp.today().date()
drivers["end_date"] = None
drivers["is_current"] = True

drivers = drivers[
    [
        "driver_id",
        "driver_name",
        "city",
        "rating",
        "effective_date",
        "end_date",
        "is_current"
    ]
]

print("Loading gold.dim_driver...")

drivers.to_sql(
    "dim_driver",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Driver Dimension Loaded Successfully!")
print("Rows:", len(drivers))