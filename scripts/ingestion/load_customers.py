import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from utils.db_connection import get_engine

engine = get_engine()

print("Reading customers.xml...")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
file_path = BASE_DIR / "data" / "raw" / "customers.xml"

if not file_path.exists():
    raise FileNotFoundError(f"Customer file not found: {file_path}")

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

customers["source_file"] = "customers.xml"
customers["batch_id"] = 1
customers["load_timestamp"] = pd.Timestamp.now()

print("Customers rows:", len(customers))
print(customers.head())

print("Clearing old bronze.customer_raw...")

with engine.begin() as conn:
    conn.exec_driver_sql("TRUNCATE TABLE bronze.customer_raw RESTART IDENTITY CASCADE")

print("Loading customers into PostgreSQL...")

customers.to_sql(
    name="customer_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi",
)

print("Customers loaded successfully!")