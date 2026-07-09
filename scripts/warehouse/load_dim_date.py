import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

dates = pd.read_sql("""
SELECT DISTINCT DATE(pickup_datetime) AS date_key
FROM silver.trip_clean
WHERE pickup_datetime IS NOT NULL
""", engine)

dates["date_key"] = pd.to_datetime(dates["date_key"])
dates["day"] = dates["date_key"].dt.day
dates["month"] = dates["date_key"].dt.month
dates["year"] = dates["date_key"].dt.year
dates["weekday"] = dates["date_key"].dt.day_name()
dates["weekend"] = dates["weekday"].isin(["Saturday", "Sunday"])

dates.to_sql(
    "dim_date",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Date Dimension Loaded Successfully!")
print("Rows:", len(dates))