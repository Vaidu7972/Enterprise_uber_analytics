import pandas as pd
from pathlib import Path
from utils.db_connection import get_engine

engine = get_engine()

print("Reading drivers.json...")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
file_path = BASE_DIR / "data" / "raw" / "drivers.json"

drivers = pd.read_json(file_path)

drivers["source_file"] = "drivers.json"
drivers["batch_id"] = 1
drivers["load_timestamp"] = pd.Timestamp.now()

print("Drivers rows:", len(drivers))
print(drivers.head())

print("Clearing old bronze.driver_raw...")

with engine.begin() as conn:
    conn.exec_driver_sql("TRUNCATE TABLE bronze.driver_raw RESTART IDENTITY CASCADE")

print("Loading drivers into PostgreSQL...")

drivers.to_sql(
    "driver_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Drivers loaded successfully!")