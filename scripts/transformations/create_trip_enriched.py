import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "create_trip_enriched"
SOURCE_NAME = "silver.trip_clean, driver_clean, customer_clean, weather_clean"
TARGET_TABLE = "silver.trip_enriched"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading un-enriched trips from silver.trip_clean...")
    query = text("""
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
        WHERE trip_id NOT IN (SELECT trip_id FROM silver.trip_enriched)
    """)

    with engine.connect() as conn:
        trips = pd.read_sql(query, conn)

    rows_read = len(trips)
    print(f"Un-enriched trips found: {rows_read}")

    if trips.empty:
        print("No new trips to enrich.")
        update_batch_success(
            batch_id=batch_id,
            rows_read=0,
            rows_inserted=0,
            rows_updated=0,
            rows_rejected=0,
        )
    else:
        drivers = pd.read_sql(
            text("""
                SELECT driver_id, driver_name, city, rating
                FROM silver.driver_clean
            """),
            engine,
        )

        customers = pd.read_sql(
            text("""
                SELECT customer_id, customer_name, city
                FROM silver.customer_clean
            """),
            engine,
        )

        weather = pd.read_sql(
            text("""
                SELECT weather_date, temperature, humidity
                FROM silver.weather_clean
            """),
            engine,
        )

        # Assign driver_id and customer_id deterministically if missing
        trips["driver_id"] = ["D" + str((int(row["trip_id"]) % 5000) + 1) for _, row in trips.iterrows()]
        trips["customer_id"] = ["C" + str((int(row["trip_id"]) % 5000) + 1) for _, row in trips.iterrows()]
        trips["weather_date"] = pd.to_datetime(trips["pickup_datetime"]).dt.date

        drivers["driver_id"] = drivers["driver_id"].astype(str)
        customers["customer_id"] = customers["customer_id"].astype(str)
        trips["driver_id"] = trips["driver_id"].astype(str)
        trips["customer_id"] = trips["customer_id"].astype(str)
        weather["weather_date"] = pd.to_datetime(weather["weather_date"]).dt.date

        print("Joining silver datasets...")
        enriched = trips.merge(drivers, on="driver_id", how="left")
        enriched = enriched.merge(
            customers, on="customer_id", how="left", suffixes=("_driver", "_customer")
        )
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
                "rating",
                "city_driver",
                "customer_id",
                "customer_name",
                "city_customer",
                "weather_date",
                "temperature",
                "humidity",
                "load_timestamp",
            ]
        ]

        enriched = enriched.rename(
            columns={
                "rating": "driver_rating",
                "city_driver": "driver_city",
                "city_customer": "customer_city",
            }
        )

        # Append to silver.trip_enriched without TRUNCATE
        print(f"Loading {len(enriched)} new enriched records into silver.trip_enriched...")
        enriched.to_sql(
            "trip_enriched",
            schema="silver",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

        rows_inserted = len(enriched)
        print("Trip enriched table updated successfully!")
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