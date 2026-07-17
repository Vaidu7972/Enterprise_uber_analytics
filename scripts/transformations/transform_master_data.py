import pandas as pd
from sqlalchemy import text

from utils.db_connection import get_engine

# Database connection
engine = get_engine()

print("Reading bronze master data...")

with engine.connect() as conn:
    drivers = pd.read_sql(text("SELECT * FROM bronze.driver_raw"), conn)
    customers = pd.read_sql(text("SELECT * FROM bronze.customer_raw"), conn)
    weather = pd.read_sql(text("SELECT * FROM bronze.weather_raw"), conn)

print("Drivers raw rows:", len(drivers))
print("Customers raw rows:", len(customers))
print("Weather raw rows:", len(weather))

print("\nCleaning drivers...")

drivers_clean = drivers.drop_duplicates(subset=["driver_id"]).copy()

drivers_clean = drivers_clean[
    (drivers_clean["rating"] >= 1) &
    (drivers_clean["rating"] <= 5)
].copy()

drivers_clean["driver_name"] = drivers_clean["driver_name"].astype(str).str.title()
drivers_clean["city"] = drivers_clean["city"].astype(str).str.title()

print("Drivers clean rows:", len(drivers_clean))

print("\nCleaning customers...")

customers_clean = customers.drop_duplicates(subset=["customer_id"]).copy()

customers_clean["customer_name"] = customers_clean["customer_name"].astype(str).str.title()
customers_clean["city"] = customers_clean["city"].astype(str).str.title()

if "gender" in customers_clean.columns:
    customers_clean["gender"] = customers_clean["gender"].astype(str).str.title()

print("Customers clean rows:", len(customers_clean))

print("\nCleaning weather...")

weather_clean = weather.drop_duplicates(subset=["weather_date"]).copy()

weather_clean["weather_date"] = pd.to_datetime(
    weather_clean["weather_date"],
    errors="coerce"
).dt.date

weather_clean = weather_clean[
    (weather_clean["humidity"] >= 0) &
    (weather_clean["humidity"] <= 100)
].copy()

print("Weather clean rows:", len(weather_clean))

print("\nClearing old silver master data...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE silver.driver_clean RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE silver.customer_clean RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE silver.weather_clean RESTART IDENTITY CASCADE"))

print("Old silver master data cleared successfully!")

print("\nLoading silver.driver_clean...")

drivers_clean.to_sql(
    "driver_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Loading silver.customer_clean...")

customers_clean.to_sql(
    "customer_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Loading silver.weather_clean...")

weather_clean.to_sql(
    "weather_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("\nMaster data transformed successfully!")
print("Drivers:", len(drivers_clean))
print("Customers:", len(customers_clean))
print("Weather:", len(weather_clean))