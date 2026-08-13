import pandas as pd
from pathlib import Path
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_drivers"
SOURCE_NAME = "drivers.json"
TARGET_TABLE = "bronze.driver_raw"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    file_path = BASE_DIR / "data" / "raw" / SOURCE_NAME

    if not file_path.exists():
        raise FileNotFoundError(f"Driver file not found: {file_path}")

    print("Reading drivers.json...")
    drivers = pd.read_json(file_path)
    rows_read = len(drivers)

    drivers["source_file"] = SOURCE_NAME
    drivers["batch_id"] = batch_id
    drivers["load_timestamp"] = pd.Timestamp.now()

    print(f"Drivers rows read: {rows_read}")

    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE bronze.driver_raw RESTART IDENTITY CASCADE")

    print("Loading drivers into PostgreSQL bronze.driver_raw...")
    drivers.to_sql(
        name="driver_raw",
        schema="bronze",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    rows_inserted = len(drivers)
    print("Drivers loaded successfully!")

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