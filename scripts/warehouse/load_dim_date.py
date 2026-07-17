import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Loading Date Dimension...")

dates = pd.read_sql(
    text("""
        SELECT DISTINCT
            DATE(pickup_datetime) AS date_key
        FROM silver.trip_clean
        WHERE pickup_datetime IS NOT NULL
        ORDER BY DATE(pickup_datetime)
    """),
    engine
)

print("Dates found from silver.trip_clean:", len(dates))

dates["date_key"] = pd.to_datetime(dates["date_key"])
dates["day"] = dates["date_key"].dt.day
dates["month"] = dates["date_key"].dt.month
dates["year"] = dates["date_key"].dt.year
dates["weekday"] = dates["date_key"].dt.day_name()
dates["week_number"] = dates["date_key"].dt.isocalendar().week.astype(int)
dates["quarter"] = dates["date_key"].dt.quarter
dates["is_weekend"] = dates["weekday"].isin(["Saturday", "Sunday"])
dates["date_key"] = dates["date_key"].dt.date

dates = dates[
    [
        "date_key",
        "day",
        "month",
        "year",
        "weekday",
        "week_number",
        "quarter",
        "is_weekend"
    ]
]

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.dim_date CASCADE"))

dates.to_sql(
    "dim_date",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Date Dimension Loaded Successfully!")
print("Rows:", len(dates))