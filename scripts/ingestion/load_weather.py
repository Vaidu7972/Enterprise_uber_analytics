import pandas as pd
from pathlib import Path
from utils.db_connection import get_engine

engine = get_engine()

print("Reading weather.csv...")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
file_path = BASE_DIR / "data" / "raw" / "weather.csv"

weather = pd.read_csv(file_path)

weather["weather_date"] = pd.to_datetime(
    weather["weather_date"],
    errors="coerce"
).dt.date

weather["source_file"] = "weather.csv"
weather["batch_id"] = 1
weather["load_timestamp"] = pd.Timestamp.now()

print("Weather rows:", len(weather))
print(weather.head())

print("Clearing old bronze.weather_raw...")

with engine.begin() as conn:
    conn.exec_driver_sql("TRUNCATE TABLE bronze.weather_raw RESTART IDENTITY CASCADE")

print("Loading weather into PostgreSQL...")

weather.to_sql(
    "weather_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Weather loaded successfully!")