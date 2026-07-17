import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Reading Silver Enriched Trips...")

trips = pd.read_sql(
    text("""
        SELECT *
        FROM silver.trip_enriched
    """),
    engine
)

print("Reading Gold Dimensions...")

drivers = pd.read_sql(
    text("""
        SELECT driver_key, driver_id
        FROM gold.dim_driver
        WHERE is_current = true
    """),
    engine
)

customers = pd.read_sql(
    text("""
        SELECT customer_key, customer_id
        FROM gold.dim_customer
    """),
    engine
)

weather = pd.read_sql(
    text("""
        SELECT weather_key, weather_date
        FROM gold.dim_weather
    """),
    engine
)

dates = pd.read_sql(
    text("""
        SELECT date_key
        FROM gold.dim_date
    """),
    engine
)

print("Preparing date columns...")

trips["pickup_datetime"] = pd.to_datetime(trips["pickup_datetime"], errors="coerce")
trips["date_key"] = trips["pickup_datetime"].dt.date

if "weather_date" in trips.columns:
    trips["weather_date"] = pd.to_datetime(trips["weather_date"], errors="coerce").dt.date
else:
    trips["weather_date"] = trips["date_key"]

weather["weather_date"] = pd.to_datetime(weather["weather_date"], errors="coerce").dt.date
dates["date_key"] = pd.to_datetime(dates["date_key"], errors="coerce").dt.date

print("Joining Dimension Keys...")

fact = trips.merge(drivers, on="driver_id", how="left")
fact = fact.merge(customers, on="customer_id", how="left")
fact = fact.merge(weather, on="weather_date", how="left")
fact = fact.merge(dates, on="date_key", how="left")

fact = fact[
    [
        "trip_id",
        "driver_key",
        "customer_key",
        "weather_key",
        "date_key",
        "fare_amount",
        "trip_distance",
        "trip_duration_minutes",
        "passenger_count"
    ]
]

fact = fact.dropna(
    subset=[
        "trip_id",
        "driver_key",
        "customer_key",
        "weather_key",
        "date_key"
    ]
)

fact["trip_id"] = fact["trip_id"].astype(int)
fact["driver_key"] = fact["driver_key"].astype(int)
fact["customer_key"] = fact["customer_key"].astype(int)
fact["weather_key"] = fact["weather_key"].astype(int)

fact = fact.drop_duplicates(subset=["trip_id"])

print("Loading Fact Table...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE"))

fact.to_sql(
    "fact_trip",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Fact Table Loaded Successfully!")
print("Rows:", len(fact))