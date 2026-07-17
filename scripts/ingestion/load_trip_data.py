import pandas as pd
from pathlib import Path
from utils.db_connection import get_engine

engine = get_engine()

print("Reading parquet file...")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
file_path = BASE_DIR / "data" / "raw" / "yellow_tripdata_2024-01.parquet"

df = pd.read_parquet(file_path)

print("Original rows:", len(df))

# Standardize column names if needed
rename_map = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "passenger_count": "passenger_count",
    "trip_distance": "trip_distance",
    "fare_amount": "fare_amount"
}

df = df.rename(columns=rename_map)

required_columns = [
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "fare_amount"
]

df = df[required_columns].copy()

df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

# Keep January 2024 only
df = df[
    (df["pickup_datetime"] >= "2024-01-01") &
    (df["pickup_datetime"] < "2024-02-01")
].copy()

# Create trip date for daily sampling
df["trip_date"] = df["pickup_datetime"].dt.date

# Take 500 trips from each day
df = (
    df.sort_values("pickup_datetime")
      .groupby("trip_date", group_keys=False)
      .head(500)
      .copy()
)

df = df.drop(columns=["trip_date"])

# Add metadata
df["source_file"] = "yellow_tripdata_2024-01.parquet"
df["batch_id"] = 1
df["load_timestamp"] = pd.Timestamp.now()

print("Rows after daily sampling:", len(df))
print("Dates loaded:", df["pickup_datetime"].dt.date.nunique())
print(df.head())

print("Clearing old bronze.trip_raw...")

with engine.begin() as conn:
    conn.exec_driver_sql("TRUNCATE TABLE bronze.trip_raw RESTART IDENTITY CASCADE")

print("Loading data into PostgreSQL...")

df.to_sql(
    "trip_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10000,
    method="multi"
)

print("Trip raw data loaded successfully!")
print("Rows loaded:", len(df))
print("Unique dates:", df["pickup_datetime"].dt.date.nunique())