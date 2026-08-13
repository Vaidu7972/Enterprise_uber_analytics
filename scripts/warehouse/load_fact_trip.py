import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_fact_trip"
SOURCE_NAME = "silver.trip_enriched"
TARGET_TABLE = "gold.fact_trip"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading unloaded trips from silver.trip_enriched...")
    trips_query = text("""
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
        WHERE trip_id NOT IN (SELECT trip_id FROM gold.fact_trip)
    """)

    trips = pd.read_sql(trips_query, engine)
    rows_read = len(trips)
    print(f"Unloaded trips found for fact_trip: {rows_read}")

    if trips.empty:
        print("No new trips to load into gold.fact_trip.")
        update_batch_success(
            batch_id=batch_id,
            rows_read=0,
            rows_inserted=0,
            rows_updated=0,
            rows_rejected=0,
        )
    else:
        # Join ONLY current driver rows (SCD Type 2 requirement)
        drivers = pd.read_sql(
            text("""
                SELECT driver_key, driver_id
                FROM gold.dim_driver
                WHERE is_current = TRUE
            """),
            engine,
        )

        customers = pd.read_sql(
            text("""
                SELECT customer_key, customer_id
                FROM gold.dim_customer
                WHERE is_current = TRUE
            """),
            engine,
        )

        weather = pd.read_sql(
            text("""
                SELECT weather_key, weather_date
                FROM gold.dim_weather
            """),
            engine,
        )

        trips["driver_id"] = trips["driver_id"].astype(str)
        trips["customer_id"] = trips["customer_id"].astype(str)
        drivers["driver_id"] = drivers["driver_id"].astype(str)
        customers["customer_id"] = customers["customer_id"].astype(str)

        weather["weather_date"] = pd.to_datetime(weather["weather_date"]).dt.date
        trips["weather_date"] = pd.to_datetime(trips["weather_date"]).dt.date

        print("Joining Dimension Keys...")
        fact = trips.merge(drivers, on="driver_id", how="left")
        fact = fact.merge(customers, on="customer_id", how="left")
        fact = fact.merge(weather, on="weather_date", how="left")

        fact["date_key"] = pd.to_datetime(fact["pickup_datetime"]).dt.date

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
                "passenger_count",
            ]
        ]

        # Fill missing dimension keys with fallback if any, drop invalid keys
        fact = fact.dropna(subset=["driver_key", "customer_key", "date_key"]).copy()
        fact["driver_key"] = fact["driver_key"].astype(int)
        fact["customer_key"] = fact["customer_key"].astype(int)

        print(f"Loading {len(fact)} rows into gold.fact_trip...")
        fact.to_sql(
            "fact_trip",
            schema="gold",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
        )

        rows_inserted = len(fact)
        print("Fact Table Loaded Successfully!")
        print("Rows loaded:", rows_inserted)

        update_batch_success(
            batch_id=batch_id,
            rows_read=rows_read,
            rows_inserted=rows_inserted,
            rows_updated=0,
            rows_rejected=0,
        )

except Exception as e:
    update_batch_failure(batch_id, str(e))
    raise e