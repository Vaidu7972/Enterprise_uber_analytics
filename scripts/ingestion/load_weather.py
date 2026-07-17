import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

df = pd.read_csv(
    "data/raw/weather.csv"
)

df["source_file"] = "weather.csv"
df["batch_id"] = 1
df["load_timestamp"] = datetime.now()

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

df.to_sql(
    name="weather_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("Weather data loaded successfully!")