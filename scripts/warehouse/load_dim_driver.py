import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_dim_driver"
SOURCE_NAME = "silver.driver_clean"
TARGET_TABLE = "gold.dim_driver"

def ensure_driver_schema():
    """Ensure UNIQUE constraint on driver_id is dropped to support SCD Type 2 history."""
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE gold.dim_driver DROP CONSTRAINT IF EXISTS dim_driver_driver_id_key;"))
        conn.execute(text("ALTER TABLE gold.dim_driver DROP CONSTRAINT IF EXISTS gold_dim_driver_driver_id_key;"))

ensure_driver_schema()

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading Driver data from silver.driver_clean...")
    drivers = pd.read_sql(
        text("""
            SELECT DISTINCT
                driver_id,
                driver_name,
                city,
                rating
            FROM silver.driver_clean
            WHERE driver_id IS NOT NULL
        """),
        engine,
    )

    drivers = drivers.drop_duplicates(subset=["driver_id"]).copy()
    rows_read = len(drivers)
    print(f"Driver records read: {rows_read}")

    # 1. Fetch current active drivers from gold.dim_driver in a single query
    with engine.connect() as conn:
        existing_rows = conn.execute(
            text("""
                SELECT driver_key, driver_id, driver_name, city, rating
                FROM gold.dim_driver
                WHERE is_current = TRUE
            """)
        ).mappings().all()

    existing_driver_map = {str(r["driver_id"]): r for r in existing_rows}

    keys_to_expire = []
    new_rows_to_insert = []
    today_date = pd.Timestamp.now().date()

    # 2. Compare incoming drivers in-memory
    for _, row in drivers.iterrows():
        drv_id = str(row["driver_id"])
        drv_name = str(row["driver_name"])
        drv_city = str(row["city"])
        drv_rating = float(row["rating"]) if pd.notnull(row["rating"]) else None

        curr = existing_driver_map.get(drv_id)

        if not curr:
            new_rows_to_insert.append({
                "driver_id": drv_id,
                "driver_name": drv_name,
                "city": drv_city,
                "rating": drv_rating,
                "effective_date": today_date,
                "end_date": None,
                "is_current": True,
            })
        else:
            is_changed = (
                curr["driver_name"] != drv_name
                or curr["city"] != drv_city
                or (curr["rating"] is not None and float(curr["rating"]) != drv_rating)
            )

            if is_changed:
                keys_to_expire.append(curr["driver_key"])
                new_rows_to_insert.append({
                    "driver_id": drv_id,
                    "driver_name": drv_name,
                    "city": drv_city,
                    "rating": drv_rating,
                    "effective_date": today_date,
                    "end_date": None,
                    "is_current": True,
                })

    rows_updated = len(keys_to_expire)
    rows_inserted = len(new_rows_to_insert)

    # 3. Perform batch updates & inserts
    with engine.begin() as conn:
        if keys_to_expire:
            print(f"Expiring {len(keys_to_expire)} outdated driver records...")
            conn.execute(
                text("""
                    UPDATE gold.dim_driver
                    SET
                        end_date = CURRENT_DATE,
                        is_current = FALSE
                    WHERE driver_key = ANY(:keys)
                """),
                {"keys": keys_to_expire},
            )

        if new_rows_to_insert:
            print(f"Inserting {len(new_rows_to_insert)} new/updated driver records...")
            df_to_insert = pd.DataFrame(new_rows_to_insert)
            df_to_insert.to_sql(
                name="dim_driver",
                schema="gold",
                con=conn,
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )

    print("Driver Dimension SCD Type 2 Load Completed Successfully!")
    print(f"Inserted (New/History): {rows_inserted}, Expired: {rows_updated}")

    update_batch_success(
        batch_id=batch_id,
        rows_read=rows_read,
        rows_inserted=rows_inserted,
        rows_updated=rows_updated,
        rows_rejected=0,
    )

except Exception as e:
    update_batch_failure(batch_id, str(e))
    raise e