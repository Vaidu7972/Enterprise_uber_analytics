import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Loading Driver Dimension...")

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

drivers = drivers.drop_duplicates(subset=["driver_id"]).copy()

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

print("Clearing old gold driver/fact data...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.driver_performance_mart RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.revenue_mart RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.kpi_summary RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.dim_driver RESTART IDENTITY CASCADE"))

print("Loading gold.dim_driver...")

drivers.to_sql(
    name="dim_driver",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Driver Dimension Loaded Successfully!")
print("Rows:", len(drivers))