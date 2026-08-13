import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_customers"
SOURCE_NAME = "customers.xml"
TARGET_TABLE = "bronze.customer_raw"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    file_path = BASE_DIR / "data" / "raw" / SOURCE_NAME

    if not file_path.exists():
        raise FileNotFoundError(f"Customer file not found: {file_path}")

    print("Reading customers.xml...")
    tree = ET.parse(file_path)
    root = tree.getroot()

    customers_data = []
    for customer in root.findall("customer"):
        customers_data.append(
            {
                "customer_id": customer.find("customer_id").text,
                "customer_name": customer.find("customer_name").text,
                "city": customer.find("city").text,
                "gender": customer.find("gender").text,
            }
        )

    customers = pd.DataFrame(customers_data)
    rows_read = len(customers)

    customers["source_file"] = SOURCE_NAME
    customers["batch_id"] = batch_id
    customers["load_timestamp"] = pd.Timestamp.now()

    print(f"Customers rows read: {rows_read}")

    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE bronze.customer_raw RESTART IDENTITY CASCADE")

    print("Loading customers into PostgreSQL bronze.customer_raw...")
    customers.to_sql(
        name="customer_raw",
        schema="bronze",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    rows_inserted = len(customers)
    print("Customers loaded successfully!")

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