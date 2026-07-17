import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

weather = pd.read_sql("""
SELECT
weather_date,
temperature,
humidity,
rainfall,
wind_speed
FROM silver.weather_clean
""", engine)

weather.to_sql(
    "dim_weather",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Weather Dimension Loaded Successfully!")
print("Rows:", len(weather))