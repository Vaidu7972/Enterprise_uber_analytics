import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "transform_master_data"
SOURCE_NAME = "bronze.driver_raw / customer_raw / weather_raw"
TARGET_TABLE = "silver.driver_clean, customer_clean, weather_clean"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading bronze master data...")
    drivers = pd.read_sql(text("SELECT * FROM bronze.driver_raw"), engine)
    customers = pd.read_sql(text("SELECT * FROM bronze.customer_raw"), engine)
    weather = pd.read_sql(text("SELECT * FROM bronze.weather_raw"), engine)

    rows_read = len(drivers) + len(customers) + len(weather)

    print("Cleaning drivers...")
    drivers_clean = drivers.drop_duplicates(subset=["driver_id"]).copy()
    drivers_clean = drivers_clean[
        (drivers_clean["rating"] >= 1) & (drivers_clean["rating"] <= 5)
    ].copy()
    drivers_clean["driver_name"] = drivers_clean["driver_name"].astype(str).str.title()
    drivers_clean["city"] = drivers_clean["city"].astype(str).str.title()
    drivers_clean["cleaned_timestamp"] = pd.Timestamp.now()

    print("Cleaning customers...")
    customers_clean = customers.drop_duplicates(subset=["customer_id"]).copy()
    customers_clean["customer_name"] = customers_clean["customer_name"].astype(str).str.title()
    customers_clean["city"] = customers_clean["city"].astype(str).str.title()
    customers_clean["gender"] = customers_clean["gender"].astype(str).str.title()
    customers_clean["cleaned_timestamp"] = pd.Timestamp.now()

    print("Cleaning weather...")
    weather_clean = weather.drop_duplicates(subset=["weather_date"]).copy()
    weather_clean["weather_date"] = pd.to_datetime(
        weather_clean["weather_date"], errors="coerce"
    ).dt.date
    weather_clean = weather_clean[
        (weather_clean["humidity"] >= 0) & (weather_clean["humidity"] <= 100)
    ].copy()
    weather_clean["cleaned_timestamp"] = pd.Timestamp.now()

    # Safely update silver master tables using ON CONFLICT / Upsert
    with engine.begin() as conn:
        print("Upserting silver.driver_clean...")
        for _, row in drivers_clean.iterrows():
            conn.execute(
                text("""
                    INSERT INTO silver.driver_clean
                    (driver_id, driver_name, city, rating, join_date, source_file, batch_id, load_timestamp, cleaned_timestamp)
                    VALUES
                    (:driver_id, :driver_name, :city, :rating, :join_date, :source_file, :batch_id, :load_timestamp, :cleaned_timestamp)
                    ON CONFLICT (driver_id) DO UPDATE SET
                        driver_name = EXCLUDED.driver_name,
                        city = EXCLUDED.city,
                        rating = EXCLUDED.rating,
                        join_date = EXCLUDED.join_date,
                        source_file = EXCLUDED.source_file,
                        batch_id = EXCLUDED.batch_id,
                        load_timestamp = EXCLUDED.load_timestamp,
                        cleaned_timestamp = EXCLUDED.cleaned_timestamp;
                """),
                {
                    "driver_id": str(row["driver_id"]),
                    "driver_name": str(row["driver_name"]),
                    "city": str(row["city"]),
                    "rating": float(row["rating"]) if pd.notnull(row["rating"]) else None,
                    "join_date": row["join_date"],
                    "source_file": str(row.get("source_file", "")),
                    "batch_id": int(row.get("batch_id", batch_id)) if pd.notnull(row.get("batch_id")) else batch_id,
                    "load_timestamp": row.get("load_timestamp"),
                    "cleaned_timestamp": row["cleaned_timestamp"],
                },
            )

        print("Upserting silver.customer_clean...")
        for _, row in customers_clean.iterrows():
            conn.execute(
                text("""
                    INSERT INTO silver.customer_clean
                    (customer_id, customer_name, gender, city, signup_date, source_file, batch_id, load_timestamp, cleaned_timestamp)
                    VALUES
                    (:customer_id, :customer_name, :gender, :city, :signup_date, :source_file, :batch_id, :load_timestamp, :cleaned_timestamp)
                    ON CONFLICT (customer_id) DO UPDATE SET
                        customer_name = EXCLUDED.customer_name,
                        gender = EXCLUDED.gender,
                        city = EXCLUDED.city,
                        signup_date = EXCLUDED.signup_date,
                        source_file = EXCLUDED.source_file,
                        batch_id = EXCLUDED.batch_id,
                        load_timestamp = EXCLUDED.load_timestamp,
                        cleaned_timestamp = EXCLUDED.cleaned_timestamp;
                """),
                {
                    "customer_id": str(row["customer_id"]),
                    "customer_name": str(row["customer_name"]),
                    "gender": str(row["gender"]),
                    "city": str(row["city"]),
                    "signup_date": row["signup_date"],
                    "source_file": str(row.get("source_file", "")),
                    "batch_id": int(row.get("batch_id", batch_id)) if pd.notnull(row.get("batch_id")) else batch_id,
                    "load_timestamp": row.get("load_timestamp"),
                    "cleaned_timestamp": row["cleaned_timestamp"],
                },
            )

        print("Upserting silver.weather_clean...")
        for _, row in weather_clean.iterrows():
            conn.execute(
                text("""
                    INSERT INTO silver.weather_clean
                    (weather_date, temperature, humidity, rainfall, wind_speed, source_file, batch_id, load_timestamp, cleaned_timestamp)
                    VALUES
                    (:weather_date, :temperature, :humidity, :rainfall, :wind_speed, :source_file, :batch_id, :load_timestamp, :cleaned_timestamp)
                    ON CONFLICT (weather_date) DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidity = EXCLUDED.humidity,
                        rainfall = EXCLUDED.rainfall,
                        wind_speed = EXCLUDED.wind_speed,
                        source_file = EXCLUDED.source_file,
                        batch_id = EXCLUDED.batch_id,
                        load_timestamp = EXCLUDED.load_timestamp,
                        cleaned_timestamp = EXCLUDED.cleaned_timestamp;
                """),
                {
                    "weather_date": row["weather_date"],
                    "temperature": float(row["temperature"]) if pd.notnull(row["temperature"]) else None,
                    "humidity": float(row["humidity"]) if pd.notnull(row["humidity"]) else None,
                    "rainfall": float(row["rainfall"]) if pd.notnull(row["rainfall"]) else None,
                    "wind_speed": float(row["wind_speed"]) if pd.notnull(row["wind_speed"]) else None,
                    "source_file": str(row.get("source_file", "")),
                    "batch_id": int(row.get("batch_id", batch_id)) if pd.notnull(row.get("batch_id")) else batch_id,
                    "load_timestamp": row.get("load_timestamp"),
                    "cleaned_timestamp": row["cleaned_timestamp"],
                },
            )

    rows_inserted = len(drivers_clean) + len(customers_clean) + len(weather_clean)
    print("Master data transformed and updated successfully!")
    print("Drivers:", len(drivers_clean))
    print("Customers:", len(customers_clean))
    print("Weather:", len(weather_clean))

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