import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/uber_dw"
)

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
LIMIT 10000
""", engine)

drivers = pd.read_sql("""
SELECT
driver_id,
driver_name,
city AS driver_city,
rating AS driver_rating
FROM silver.driver_clean
""", engine)

customers = pd.read_sql("""
SELECT
customer_id,
customer_name,
city AS customer_city
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

weather["weather_date"] = pd.to_datetime(weather["weather_date"]).dt.date

print("Joining data...")

enriched = trips.merge(drivers, on="driver_id", how="left")
enriched = enriched.merge(customers, on="customer_id", how="left")
enriched = enriched.merge(weather, on="weather_date", how="left")

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
        "driver_rating",
        "driver_city",
        "customer_id",
        "customer_name",
        "customer_city",
        "weather_date",
        "temperature",
        "humidity",
        "load_timestamp"
    ]
]

print("Loading trip_enriched...")

enriched.to_sql(
    "trip_enriched",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Trip enriched table created successfully!")
print("Rows loaded:", len(enriched))