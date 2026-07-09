import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Starting SCD Type 1 for Driver Dimension...")

# Incoming updated driver data
# In real projects this comes from source system / API / new file
driver_updates = pd.DataFrame([
    {
        "driver_id": "D1",
        "driver_name": "Updated Driver One",
        "city": "New York",
        "rating": 4.95
    },
    {
        "driver_id": "D2",
        "driver_name": "Updated Driver Two",
        "city": "Boston",
        "rating": 4.80
    },
    {
        "driver_id": "D3",
        "driver_name": "Updated Driver Three",
        "city": "Chicago",
        "rating": 4.70
    }
])

with engine.begin() as conn:
    for _, row in driver_updates.iterrows():

        # Check if driver already exists
        existing_driver = conn.execute(
            text("""
                SELECT driver_key
                FROM gold.dim_driver
                WHERE driver_id = :driver_id
            """),
            {"driver_id": row["driver_id"]}
        ).fetchone()

        if existing_driver:
            # SCD Type 1: overwrite old values
            conn.execute(
                text("""
                    UPDATE gold.dim_driver
                    SET
                        driver_name = :driver_name,
                        city = :city,
                        rating = :rating,
                        effective_date = CURRENT_DATE,
                        end_date = NULL,
                        is_current = TRUE
                    WHERE driver_id = :driver_id
                """),
                {
                    "driver_id": row["driver_id"],
                    "driver_name": row["driver_name"],
                    "city": row["city"],
                    "rating": row["rating"]
                }
            )

            print(f"Updated driver: {row['driver_id']}")

        else:
            # Insert new driver if not present
            conn.execute(
                text("""
                    INSERT INTO gold.dim_driver
                    (
                        driver_id,
                        driver_name,
                        city,
                        rating,
                        effective_date,
                        end_date,
                        is_current
                    )
                    VALUES
                    (
                        :driver_id,
                        :driver_name,
                        :city,
                        :rating,
                        CURRENT_DATE,
                        NULL,
                        TRUE
                    )
                """),
                {
                    "driver_id": row["driver_id"],
                    "driver_name": row["driver_name"],
                    "city": row["city"],
                    "rating": row["rating"]
                }
            )

            print(f"Inserted new driver: {row['driver_id']}")

print("SCD Type 1 Driver Dimension completed successfully!")