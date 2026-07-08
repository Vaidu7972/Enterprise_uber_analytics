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
clean_df["trip_duration_minutes"] = (
    clean_df["dropoff_datetime"] -
    clean_df["pickup_datetime"]
).dt.total_seconds() / 60    
    