import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_dim_customer"
SOURCE_NAME = "silver.customer_clean"
TARGET_TABLE = "gold.dim_customer"

def ensure_customer_schema():
    """Auto-migrate gold.dim_customer schema if missing columns exist in target database."""
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE gold.dim_customer ADD COLUMN IF NOT EXISTS previous_city VARCHAR(100);"))
        conn.execute(text("ALTER TABLE gold.dim_customer ADD COLUMN IF NOT EXISTS city_change_date DATE;"))

ensure_customer_schema()

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading Customer data from silver.customer_clean...")
    customers = pd.read_sql(
        text("""
            SELECT DISTINCT
                customer_id,
                customer_name,
                city,
                gender
            FROM silver.customer_clean
            WHERE customer_id IS NOT NULL
        """),
        engine,
    )

    customers = customers.drop_duplicates(subset=["customer_id"]).copy()
    rows_read = len(customers)
    print(f"Customer records read: {rows_read}")

    # 1. Fetch existing customers from gold.dim_customer in a single query
    with engine.connect() as conn:
        existing_rows = conn.execute(
            text("""
                SELECT customer_key, customer_id, customer_name, city, gender, previous_city, city_change_date
                FROM gold.dim_customer
            """)
        ).mappings().all()

    existing_cust_map = {str(r["customer_id"]): r for r in existing_rows}

    new_customers_to_insert = []
    customers_to_update = []
    today_date = pd.Timestamp.now().date()

    # 2. Compare incoming customers in-memory
    for _, row in customers.iterrows():
        cust_id = str(row["customer_id"])
        cust_name = str(row["customer_name"])
        cust_city = str(row["city"])
        cust_gender = str(row["gender"])

        curr = existing_cust_map.get(cust_id)

        if not curr:
            new_customers_to_insert.append({
                "customer_id": cust_id,
                "customer_name": cust_name,
                "city": cust_city,
                "gender": cust_gender,
                "effective_date": today_date,
                "end_date": None,
                "is_current": True,
                "previous_city": None,
                "city_change_date": None,
            })
        else:
            curr_city = str(curr["city"]) if curr["city"] is not None else ""
            curr_name = str(curr["customer_name"]) if curr["customer_name"] is not None else ""
            curr_gender = str(curr["gender"]) if curr["gender"] is not None else ""

            city_changed = curr_city != cust_city
            name_or_gender_changed = (curr_name != cust_name) or (curr_gender != cust_gender)

            if city_changed or name_or_gender_changed:
                if city_changed:
                    new_prev_city = curr_city
                    new_c_city = cust_city
                    new_change_date = today_date
                else:
                    new_prev_city = curr["previous_city"]
                    new_c_city = curr_city
                    new_change_date = curr["city_change_date"]

                customers_to_update.append({
                    "customer_id": cust_id,
                    "customer_name": cust_name,
                    "gender": cust_gender,
                    "city": new_c_city,
                    "previous_city": new_prev_city,
                    "city_change_date": new_change_date,
                })

    rows_inserted = len(new_customers_to_insert)
    rows_updated = len(customers_to_update)

    # 3. Perform batch inserts & updates using executemany / bulk statements
    with engine.begin() as conn:
        if customers_to_update:
            print(f"Bulk updating {len(customers_to_update)} customer records (SCD Type 1 & 3)...")
            conn.execute(
                text("""
                    UPDATE gold.dim_customer
                    SET
                        customer_name = :customer_name,
                        gender = :gender,
                        city = :city,
                        previous_city = :previous_city,
                        city_change_date = :city_change_date,
                        is_current = TRUE
                    WHERE customer_id = :customer_id
                """),
                customers_to_update,
            )

        if new_customers_to_insert:
            print(f"Bulk inserting {len(new_customers_to_insert)} new customer records...")
            df_to_insert = pd.DataFrame(new_customers_to_insert)
            df_to_insert.to_sql(
                name="dim_customer",
                schema="gold",
                con=conn,
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )

    print("Customer Dimension SCD Type 1 & Type 3 Load Completed Successfully!")
    print(f"Inserted: {rows_inserted}, Updated: {rows_updated}")

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