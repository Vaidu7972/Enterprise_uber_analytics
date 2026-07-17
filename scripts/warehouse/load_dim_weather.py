import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Loading Weather Dimension...")

weather = pd.read_sql(
    text("""
        SELECT DISTINCT
            weather_date,
            temperature,
            humidity,
            rainfall,
            wind_speed
        FROM silver.weather_clean
        WHERE weather_date IS NOT NULL
        ORDER BY weather_date
    """),
    engine
)

weather["weather_date"] = pd.to_datetime(
    weather["weather_date"],
    errors="coerce"
).dt.date

weather = weather.drop_duplicates(subset=["weather_date"])

weather = weather[
    [
        "weather_date",
        "temperature",
        "humidity",
        "rainfall",
        "wind_speed"
    ]
]

print("Clearing old gold.dim_weather data...")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE gold.dim_weather RESTART IDENTITY CASCADE"))

print("Loading gold.dim_weather...")

weather.to_sql(
    "dim_weather",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Weather Dimension Loaded Successfully!")
print("Rows:", len(weather))