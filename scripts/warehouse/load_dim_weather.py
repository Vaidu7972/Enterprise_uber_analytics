import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_dim_weather"
SOURCE_NAME = "silver.weather_clean"
TARGET_TABLE = "gold.dim_weather"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading Weather data from silver.weather_clean...")
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
        engine,
    )

    weather["weather_date"] = pd.to_datetime(weather["weather_date"], errors="coerce").dt.date
    weather = weather.drop_duplicates(subset=["weather_date"]).copy()
    rows_read = len(weather)
    print(f"Weather records read: {rows_read}")

    rows_inserted = 0
    with engine.begin() as conn:
        for _, row in weather.iterrows():
            result = conn.execute(
                text("""
                    INSERT INTO gold.dim_weather
                    (weather_date, temperature, humidity, rainfall, wind_speed)
                    VALUES
                    (:weather_date, :temperature, :humidity, :rainfall, :wind_speed)
                    ON CONFLICT (weather_date) DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidity = EXCLUDED.humidity,
                        rainfall = EXCLUDED.rainfall,
                        wind_speed = EXCLUDED.wind_speed;
                """),
                {
                    "weather_date": row["weather_date"],
                    "temperature": float(row["temperature"]) if pd.notnull(row["temperature"]) else None,
                    "humidity": float(row["humidity"]) if pd.notnull(row["humidity"]) else None,
                    "rainfall": float(row["rainfall"]) if pd.notnull(row["rainfall"]) else None,
                    "wind_speed": float(row["wind_speed"]) if pd.notnull(row["wind_speed"]) else None,
                },
            )
            rows_inserted += result.rowcount

    print("Weather Dimension Loaded Successfully!")
    print(f"Upserted rows: {rows_inserted}")

    update_batch_success(
        batch_id=batch_id,
        rows_read=rows_read,
        rows_inserted=rows_inserted,
        rows_updated=0,
        rows_rejected=0,
    )

except Exception as e:
    update_batch_failure(batch_id, str(e))
    raise e