from sqlalchemy import text
import pandas as pd

from utils.db_connection import get_engine

# Database connection
engine = get_engine()

print("Reading Bronze Layer...")

# Read only sample while developing
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

# Convert datetime columns safely
df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

# Create rejected records dataframe
rejected_df = df[
    (df["fare_amount"] <= 0) |
    (df["trip_distance"] <= 0) |
    (df["pickup_datetime"].isnull()) |
    (df["dropoff_datetime"].isnull())
].copy()

rejected_df["rejection_reason"] = "Invalid fare, distance, or missing datetime"

# Keep only valid records
clean_df = df[
    (df["fare_amount"] > 0) &
    (df["trip_distance"] > 0) &
    (df["pickup_datetime"].notnull()) &
    (df["dropoff_datetime"].notnull())
].copy()

print("Valid Records :", len(clean_df))
print("Rejected Records :", len(rejected_df))

# Create trip_id if not available
if "trip_id" not in clean_df.columns:
    clean_df = clean_df.reset_index(drop=True)
    clean_df.insert(0, "trip_id", clean_df.index + 1)

if "trip_id" not in rejected_df.columns:
    rejected_df = rejected_df.reset_index(drop=True)
    rejected_df.insert(0, "trip_id", rejected_df.index + 1)

# Calculate trip duration
clean_df["trip_duration_minutes"] = (
    clean_df["dropoff_datetime"] -
    clean_df["pickup_datetime"]
).dt.total_seconds() / 60

print("\nTrip Duration Created Successfully!")
print(
    clean_df[
        [
            "pickup_datetime",
            "dropoff_datetime",
            "trip_duration_minutes"
        ]
    ].head()
)

# Remove duplicate trips
before_duplicates = len(clean_df)

clean_df = clean_df.drop_duplicates(subset=["trip_id"])

after_duplicates = len(clean_df)

print("\nDuplicate Removal Completed")
print("Before removing duplicates:", before_duplicates)
print("After removing duplicates :", after_duplicates)
print("Duplicates removed        :", before_duplicates - after_duplicates)

print("\nRejected Records Created")
print("Rejected Records:", len(rejected_df))
print(rejected_df.head())

# Required columns for silver.trip_clean
clean_columns = [
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
    "load_timestamp"
]

# Add missing columns safely
for col in clean_columns:
    if col not in clean_df.columns:
        clean_df[col] = None

clean_df = clean_df[clean_columns]

# Required columns for silver.trip_rejected
rejected_columns = [
    "trip_id",
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "rejection_reason"
]

# Add missing columns safely
for col in rejected_columns:
    if col not in rejected_df.columns:
        rejected_df[col] = None

rejected_df = rejected_df[rejected_columns]

print("\nClearing old silver data...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE silver.trip_clean RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE silver.trip_rejected RESTART IDENTITY CASCADE"))

print("\nLoading clean records into silver.trip_clean...")

clean_df.to_sql(
    name="trip_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10000,
    method="multi"
)

print("Loading rejected records into silver.trip_rejected...")

rejected_df.to_sql(
    name="trip_rejected",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10000,
    method="multi"
)

print("\nSilver Layer Load Completed Successfully!")
print("Clean records loaded   :", len(clean_df))
print("Rejected records loaded:", len(rejected_df))