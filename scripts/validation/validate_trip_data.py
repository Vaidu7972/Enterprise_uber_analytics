import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Validating trip data...")

df = pd.read_sql(
    text("""
        SELECT *
        FROM bronze.trip_raw
        LIMIT 10000
    """),
    engine,
)

validation_errors = []

if df.empty:
    validation_errors.append("bronze.trip_raw is empty")

invalid_fare = df[df["fare_amount"] <= 0]
invalid_distance = df[df["trip_distance"] <= 0]
missing_pickup = df[df["pickup_datetime"].isnull()]
missing_dropoff = df[df["dropoff_datetime"].isnull()]

print("Total rows checked:", len(df))
print("Invalid fare rows:", len(invalid_fare))
print("Invalid distance rows:", len(invalid_distance))
print("Missing pickup datetime rows:", len(missing_pickup))
print("Missing dropoff datetime rows:", len(missing_dropoff))

report = pd.DataFrame(
    {
        "check_name": [
            "invalid_fare",
            "invalid_distance",
            "missing_pickup_datetime",
            "missing_dropoff_datetime",
        ],
        "failed_rows": [
            len(invalid_fare),
            len(invalid_distance),
            len(missing_pickup),
            len(missing_dropoff),
        ],
    }
)

report.to_csv("docs/validation_reports/trip_validation_report.csv", index=False)

print("Validation report created successfully!")