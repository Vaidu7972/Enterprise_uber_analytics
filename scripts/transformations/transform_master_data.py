import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

print("Reading bronze master data...")

drivers = pd.read_sql("SELECT * FROM bronze.driver_raw", engine)
customers = pd.read_sql("SELECT * FROM bronze.customer_raw", engine)
weather = pd.read_sql("SELECT * FROM bronze.weather_raw", engine)

print("Cleaning drivers...")
drivers_clean = drivers.drop_duplicates(subset=["driver_id"]).copy()
drivers_clean = drivers_clean[
    (drivers_clean["rating"] >= 1) &
    (drivers_clean["rating"] <= 5)
]
drivers_clean["driver_name"] = drivers_clean["driver_name"].str.title()
drivers_clean["city"] = drivers_clean["city"].str.title()

print("Cleaning customers...")
customers_clean = customers.drop_duplicates(subset=["customer_id"]).copy()
customers_clean["customer_name"] = customers_clean["customer_name"].str.title()
customers_clean["city"] = customers_clean["city"].str.title()
customers_clean["gender"] = customers_clean["gender"].str.title()

print("Cleaning weather...")
weather_clean = weather.drop_duplicates(subset=["weather_date"]).copy()
weather_clean = weather_clean[
    (weather_clean["humidity"] >= 0) &
    (weather_clean["humidity"] <= 100)
]

print("Loading silver tables...")

drivers_clean.to_sql(
    "driver_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

customers_clean.to_sql(
    "customer_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

weather_clean.to_sql(
    "weather_clean",
    schema="silver",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Master data transformed successfully!")
print("Drivers:", len(drivers_clean))
print("Customers:", len(customers_clean))
print("Weather:", len(weather_clean))