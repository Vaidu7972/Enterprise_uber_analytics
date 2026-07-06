import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

print("Reading drivers.json...")

df = pd.read_json("data/raw/drivers.json")

print("Rows:", len(df))

df["source_file"] = "drivers.json"
df["batch_id"] = 1
df["load_timestamp"] = datetime.now()

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

print("Loading driver data...")

df.to_sql(
    name="driver_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("Driver data loaded successfully!")