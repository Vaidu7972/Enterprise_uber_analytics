import pandas as pd
from pathlib import Path
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_weather"
SOURCE_NAME = "weather.csv"
TARGET_TABLE = "bronze.weather_raw"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    file_path = BASE_DIR / "data" / "raw" / SOURCE_NAME

    if not file_path.exists():
        raise FileNotFoundError(f"Weather file not found: {file_path}")

    print("Reading weather.csv...")
    weather = pd.read_csv(file_path)

    weather["weather_date"] = pd.to_datetime(
        weather["weather_date"],
        errors="coerce",
    ).dt.date

    rows_read = len(weather)
    weather["source_file"] = SOURCE_NAME
    weather["batch_id"] = batch_id
    weather["load_timestamp"] = pd.Timestamp.now()

    print(f"Weather rows read: {rows_read}")

    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE bronze.weather_raw RESTART IDENTITY CASCADE")

    print("Loading weather into PostgreSQL bronze.weather_raw...")
    weather.to_sql(
        name="weather_raw",
        schema="bronze",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    rows_inserted = len(weather)
    print("Weather loaded successfully!")

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