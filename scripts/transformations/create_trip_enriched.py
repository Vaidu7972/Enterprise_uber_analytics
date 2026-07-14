import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

print("Reading silver tables...")

trips = pd.read_sql("""
SELECT
    trip_id,
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    trip_duration_minutes,
    load_timestamp
FROM silver.trip_clean
""", engine)

drivers = pd.read_sql("""
SELECT
    driver_id,
    driver_name,
    city,
    rating
FROM silver.driver_clean
""", engine)

customers = pd.read_sql("""
SELECT
    customer_id,
    customer_name,
    city
FROM silver.customer_clean
""", engine)

weather = pd.read_sql("""
SELECT
    weather_date,
    temperature,
    humidity
FROM silver.weather_clean
""", engine)

print("Assigning driver and customer ids...")

trips["driver_id"] = ["D" + str((i % 5000) + 1) for i in range(len(trips))]
trips["customer_id"] = ["C" + str((i % 5000) + 1) for i in range(len(trips))]
trips["weather_date"] = pd.to_datetime(trips["pickup_datetime"]).dt.date

drivers["driver_id"] = drivers["driver_id"].astype(str)
customers["customer_id"] = customers["customer_id"].astype(str)

trips["driver_id"] = trips["driver_id"].astype(str)
trips["customer_id"] = trips["customer_id"].astype(str)

weather["weather_date"] = pd.to_datetime(weather["weather_date"]).dt.date

print("Joining data...")

enriched = trips.merge(
    drivers,
    on="driver_id",
    how="left"
)

enriched = enriched.merge(
    customers,
    on="customer_id",
    how="left",
    suffixes=("_driver", "_customer")
)

enriched = enriched.merge(
    weather,
    on="weather_date",
    how="left"
)

enriched = enriched[
    [
        "trip_id",
        "vendor_id",
        "pickup_datetime",
        "dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "trip_duration_minutes",

        "driver_id",
        "driver_name",
        "rating",
        "city_driver",

        "customer_id",
        "customer_name",
        "city_customer",

        "weather_date",
        "temperature",
        "humidity",
        "load_timestamp"
    ]
]

enriched = enriched.rename(
    columns={
        "rating": "driver_rating",
        "city_driver": "driver_city",
        "city_customer": "customer_city"
    }
)

print("Rows to load:", len(enriched))

print("Clearing old silver.trip_enriched data...")

with engine.begin() as conn:
    conn.exec_driver_sql("TRUNCATE TABLE silver.trip_enriched;")

print("Loading trip_enriched...")

enriched.to_sql(
    "trip_enriched",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Trip enriched table created successfully!")
print("Rows loaded:", len(enriched))