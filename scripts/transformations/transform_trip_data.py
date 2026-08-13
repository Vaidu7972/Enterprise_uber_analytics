import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "transform_trip_data"
SOURCE_NAME = "bronze.trip_raw"
TARGET_TABLE = "silver.trip_clean"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading unprocessed records from Bronze Layer...")
    query = text("""
        SELECT *
        FROM bronze.trip_raw
        WHERE trip_id NOT IN (
            SELECT trip_id FROM silver.trip_clean
            UNION ALL
            SELECT trip_id FROM silver.trip_rejected
        )
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    rows_read = len(df)
    print(f"Unprocessed Bronze records found: {rows_read}")

    if df.empty:
        print("No new trip records to transform.")
        update_batch_success(
            batch_id=batch_id,
            rows_read=0,
            rows_inserted=0,
            rows_updated=0,
            rows_rejected=0,
        )
    else:
        required_columns = [
            "vendor_id",
            "pickup_datetime",
            "dropoff_datetime",
            "passenger_count",
            "trip_distance",
            "fare_amount",
            "source_file",
            "batch_id",
            "load_timestamp",
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in bronze.trip_raw: {missing_columns}")

        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
        df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

        # Validate rows
        valid_condition = (
            (df["fare_amount"] > 0)
            & (df["trip_distance"] > 0)
            & (df["pickup_datetime"].notnull())
            & (df["dropoff_datetime"].notnull())
        )

        clean_df = df[valid_condition].copy()
        rejected_df = df[~valid_condition].copy()

        # Clean transformations
        clean_df["trip_duration_minutes"] = (
            clean_df["dropoff_datetime"] - clean_df["pickup_datetime"]
        ).dt.total_seconds() / 60

        clean_df = clean_df.drop_duplicates(subset=["trip_id"])
        clean_df["cleaned_timestamp"] = pd.Timestamp.now()

        clean_df = clean_df[
            [
                "trip_id",
                "vendor_id",
                "pickup_datetime",
                "dropoff_datetime",
                "passenger_count",
                "trip_distance",
                "fare_amount",
                "trip_duration_minutes",
                "source_file",
                "batch_id",
                "load_timestamp",
                "cleaned_timestamp",
            ]
        ]

        # Rejected transformations
        rejected_df["rejection_reason"] = "Invalid fare, distance, or missing datetime"
        rejected_df["rejected_timestamp"] = pd.Timestamp.now()

        rejected_df = rejected_df[
            [
                "trip_id",
                "vendor_id",
                "pickup_datetime",
                "dropoff_datetime",
                "passenger_count",
                "trip_distance",
                "fare_amount",
                "rejection_reason",
                "rejected_timestamp",
            ]
        ]

        # Append to silver.trip_clean without TRUNCATE
        print(f"Loading {len(clean_df)} clean records into silver.trip_clean...")
        clean_df.to_sql(
            name="trip_clean",
            schema="silver",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

        # Append to silver.trip_rejected without TRUNCATE
        print(f"Loading {len(rejected_df)} rejected records into silver.trip_rejected...")
        rejected_df.to_sql(
            name="trip_rejected",
            schema="silver",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

        print("\nSilver Trip Layer Transformation Completed Successfully!")
        print("Clean rows inserted:", len(clean_df))
        print("Rejected rows inserted:", len(rejected_df))

        update_batch_success(
            batch_id=batch_id,
            rows_read=rows_read,
            rows_inserted=len(clean_df),
            rows_updated=0,
            rows_rejected=len(rejected_df),
        )

except Exception as e:
    update_batch_failure(batch_id, str(e))
    raise e