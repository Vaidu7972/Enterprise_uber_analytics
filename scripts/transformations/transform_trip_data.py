import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Reading Bronze Layer...")

query = text("""
WITH daily_sample AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY DATE(pickup_datetime)
               ORDER BY pickup_datetime
           ) AS rn
    FROM bronze.trip_raw
    WHERE pickup_datetime >= '2024-01-01'
      AND pickup_datetime < '2024-02-01'
)
SELECT *
FROM daily_sample
WHERE rn <= 500
""")

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

if "rn" in df.columns:
    df = df.drop(columns=["rn"])

print(df.head())
print(df.shape)

print("\nCleaning Data...")

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

# Create trip_id if not available
if "trip_id" not in df.columns:
    df = df.reset_index(drop=True)
    df.insert(0, "trip_id", df.index + 1)

valid_condition = (
    (df["fare_amount"] > 0) &
    (df["trip_distance"] > 0) &
    (df["pickup_datetime"].notnull()) &
    (df["dropoff_datetime"].notnull())
)

clean_df = df[valid_condition].copy()
rejected_df = df[~valid_condition].copy()

print("Valid Records:", len(clean_df))
print("Rejected Records:", len(rejected_df))

clean_df["trip_duration_minutes"] = (
    clean_df["dropoff_datetime"] -
    clean_df["pickup_datetime"]
).dt.total_seconds() / 60

print("\nTrip Duration Created Successfully!")

before_duplicates = len(clean_df)
clean_df = clean_df.drop_duplicates(subset=["trip_id"])
after_duplicates = len(clean_df)

print("\nDuplicate Removal Completed")
print("Before removing duplicates:", before_duplicates)
print("After removing duplicates:", after_duplicates)
print("Duplicates removed:", before_duplicates - after_duplicates)

rejected_df["rejection_reason"] = "Invalid fare, distance, or missing datetime"

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
    ]
]

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
    ]
]

print("Clearing old silver trip tables...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE silver.trip_enriched CASCADE"))
    conn.execute(text("TRUNCATE TABLE silver.trip_clean RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE silver.trip_rejected RESTART IDENTITY CASCADE"))

print("Loading clean records into silver.trip_clean...")

clean_df.to_sql(
    name="trip_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi",
)

print("Loading rejected records into silver.trip_rejected...")

rejected_df.to_sql(
    name="trip_rejected",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi",
)

print("\nSilver Trip Layer Load Completed Successfully!")
print("Clean rows:", len(clean_df))
print("Rejected rows:", len(rejected_df))