import os
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

# Check if demo mode is enabled via environment variable
is_demo_mode = os.getenv("INCREMENTAL_DEMO_MODE", "false").lower() in ("true", "1", "yes")

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_trip_data"
SOURCE_NAME = "incremental_demo_trip.csv" if is_demo_mode else "yellow_tripdata_2024-01.parquet"
TARGET_TABLE = "bronze.trip_raw"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    # 1. Get last loaded watermark from target table bronze.trip_raw
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(pickup_datetime) FROM bronze.trip_raw")).scalar()
        last_watermark = pd.to_datetime(result) if result is not None else None

    print(f"Last watermark from bronze.trip_raw: {last_watermark}")

    # 2. Read source data
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    file_path = BASE_DIR / "data" / "raw" / SOURCE_NAME

    if not file_path.exists():
        raise FileNotFoundError(f"Trip source file not found: {file_path}")

    if is_demo_mode:
        print(f"[DEMO MODE] Reading incremental demo CSV file ({SOURCE_NAME})...")
        df = pd.read_csv(file_path)
    else:
        print(f"Reading parquet file ({SOURCE_NAME})...")
        df = pd.read_parquet(file_path)
        df = df[
            [
                "VendorID",
                "tpep_pickup_datetime",
                "tpep_dropoff_datetime",
                "passenger_count",
                "trip_distance",
                "fare_amount",
            ]
        ].copy()
        df = df.rename(
            columns={
                "VendorID": "vendor_id",
                "tpep_pickup_datetime": "pickup_datetime",
                "tpep_dropoff_datetime": "dropoff_datetime",
            }
        )

    # Convert datetime
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

    if not is_demo_mode:
        # Production filtering for January 2024 and 500 daily sampling
        df = df[
            (df["pickup_datetime"] >= "2024-01-01")
            & (df["pickup_datetime"] < "2024-02-01")
        ].copy()
        df["trip_date"] = df["pickup_datetime"].dt.date
        df = (
            df.sort_values("pickup_datetime")
            .groupby("trip_date", group_keys=False)
            .head(500)
            .copy()
        )
        df = df.drop(columns=["trip_date"])

    rows_read = len(df)

    # 3. Watermark filtering: pickup_datetime > last_watermark
    if last_watermark is not None:
        df = df[df["pickup_datetime"] > last_watermark].copy()

    print(f"Rows to insert after watermark filter (pickup_datetime > {last_watermark}): {len(df)}")

    if df.empty:
        print("No new records to insert into bronze.trip_raw.")
        update_batch_success(
            batch_id=batch_id,
            rows_read=rows_read,
            rows_inserted=0,
            rows_updated=0,
            rows_rejected=0,
            last_watermark=last_watermark,
        )
    else:
        new_max_watermark = df["pickup_datetime"].max()

        # Metadata tracking
        df["source_file"] = SOURCE_NAME
        df["batch_id"] = batch_id
        df["load_timestamp"] = pd.Timestamp.now()

        df = df[
            [
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
        ]

        # 4. Append only new records (No TRUNCATE)
        print("Appending new records into bronze.trip_raw...")
        df.to_sql(
            name="trip_raw",
            schema="bronze",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=10000,
            method="multi",
        )

        rows_inserted = len(df)
        print(f"Successfully loaded {rows_inserted} incremental rows into bronze.trip_raw!")
        print(f"New Watermark: {new_max_watermark}")

        update_batch_success(
            batch_id=batch_id,
            rows_read=rows_read,
            rows_inserted=rows_inserted,
            rows_updated=0,
            rows_rejected=0,
            last_watermark=new_max_watermark,
        )

except Exception as e:
    update_batch_failure(batch_id, str(e))
    raise e