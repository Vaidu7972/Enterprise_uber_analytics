from sqlalchemy import create_engine
import pandas as pd
import os

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

df = pd.read_sql(
    "SELECT * FROM bronze.trip_raw LIMIT 10000",
    engine
)

print("Data loaded for validation")
print(df.shape)

# 1. Null check
null_values = df.isnull().sum()
print("\nNull Values:")
print(null_values)

# 2. Invalid fare check
invalid_fare = df[df["fare_amount"] <= 0]
print("\nInvalid Fare Records:", len(invalid_fare))

# 3. Invalid distance check
invalid_distance = df[df["trip_distance"] <= 0]
print("Invalid Distance Records:", len(invalid_distance))

# 4. Duplicate check
duplicate_trips = df.duplicated(subset=["trip_id"]).sum()
print("Duplicate Trips:", duplicate_trips)

# 5. Save report
os.makedirs("docs/validation_reports", exist_ok=True)

report = {
    "total_records_checked": len(df),
    "total_null_values": int(null_values.sum()),
    "invalid_fare_records": len(invalid_fare),
    "invalid_distance_records": len(invalid_distance),
    "duplicate_trips": int(duplicate_trips)
}

report_df = pd.DataFrame([report])

report_df.to_csv(
    "docs/validation_reports/trip_validation_report.csv",
    index=False
)

print("\nValidation report saved successfully!")