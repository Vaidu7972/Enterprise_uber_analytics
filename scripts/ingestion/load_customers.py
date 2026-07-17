import pandas as pd
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from datetime import datetime

tree = ET.parse("data/raw/customers.xml")
root = tree.getroot()

rows = []

for customer in root.findall("customer"):
    rows.append({
        "customer_id": customer.find("customer_id").text,
        "customer_name": customer.find("customer_name").text,
        "gender": customer.find("gender").text,
        "city": customer.find("city").text,
        "signup_date": customer.find("signup_date").text
    })

df = pd.DataFrame(rows)

df["source_file"] = "customers.xml"
df["batch_id"] = 1
df["load_timestamp"] = datetime.now()

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

df.to_sql(
    name="customer_raw",
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("Customer data loaded successfully!")