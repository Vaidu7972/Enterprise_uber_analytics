import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

print("Reading Gold Dimensions...")

trips = pd.read_sql("""
SELECT
trip_id,
driver_id,
customer_id,
weather_date,
pickup_datetime,
fare_amount,
trip_distance,
trip_duration_minutes,
passenger_count
FROM silver.trip_enriched
""", engine)

drivers = pd.read_sql("""
SELECT
driver_key,
driver_id
FROM gold.dim_driver
""", engine)

customers = pd.read_sql("""
SELECT
customer_key,
customer_id
FROM gold.dim_customer
""", engine)

weather = pd.read_sql("""
SELECT
weather_key,
weather_date
FROM gold.dim_weather
""", engine)

print("Joining Dimension Keys...")

fact = trips.merge(
    drivers,
    on="driver_id",
    how="left"
)

fact = fact.merge(
    customers,
    on="customer_id",
    how="left"
)

fact = fact.merge(
    weather,
    on="weather_date",
    how="left"
)

fact["date_key"] = pd.to_datetime(
    fact["pickup_datetime"]
).dt.date

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

print("Loading Fact Table...")

fact.to_sql(
    "fact_trip",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Fact Table Loaded Successfully!")
print("Rows:", len(fact))