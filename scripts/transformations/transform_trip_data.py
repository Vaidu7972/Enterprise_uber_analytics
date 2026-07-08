from sqlalchemy import create_engine
import pandas as pd

# Database connection
engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

print("Reading Bronze Layer...")

# Read only a sample while developing
df = pd.read_sql(
    "SELECT * FROM bronze.trip_raw LIMIT 10000",
    engine
)

print(df.head())
print(df.shape)

#to remove invalid data
print("\nCleaning Data...")

# Keep only valid fare and distance
clean_df = df[
    (df["fare_amount"] > 0) &
    (df["trip_distance"] > 0)
].copy()

print("Valid Records :", len(clean_df))
print("Rejected Records :", len(df) - len(clean_df))

"""Business rule:

Fare must be greater than 0
Distance must be greater than 0
"""
    
#calculating trip duration
# Convert columns to datetime
clean_df["pickup_datetime"] = pd.to_datetime(clean_df["pickup_datetime"])
clean_df["dropoff_datetime"] = pd.to_datetime(clean_df["dropoff_datetime"])

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

# Step 7: Remove duplicate trips
before_duplicates = len(clean_df)

clean_df = clean_df.drop_duplicates(subset=["trip_id"])

after_duplicates = len(clean_df)

print("\nDuplicate Removal Completed")
print("Before removing duplicates:", before_duplicates)
print("After removing duplicates :", after_duplicates)
print("Duplicates removed        :", before_duplicates - after_duplicates)

# Step 8: Create rejected records dataframe
rejected_df = df[
    (df["fare_amount"] <= 0) |
    (df["trip_distance"] <= 0) |
    (df["pickup_datetime"].isnull()) |
    (df["dropoff_datetime"].isnull())
].copy()

rejected_df["rejection_reason"] = "Invalid fare, distance, or missing datetime"

print("\nRejected Records Created")
print("Rejected Records:", len(rejected_df))

print(rejected_df.head())

# Keep only columns needed for silver.trip_clean
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
        "load_timestamp"
    ]
]

# Keep only columns needed for silver.trip_rejected
rejected_df = rejected_df[
    [
        "trip_id",
        "vendor_id",
        "pickup_datetime",
        "dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "rejection_reason"
    ]
]

print("\nLoading clean records into silver.trip_clean...")
clean_df.to_sql(
    name="trip_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("Loading rejected records into silver.trip_rejected...")
rejected_df.to_sql(
    name="trip_rejected",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("\nSilver Layer Load Completed Successfully!")

