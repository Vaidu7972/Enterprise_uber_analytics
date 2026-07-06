import pandas as pd  # Import Pandas library for working with table-like data
from sqlalchemy import create_engine  # Import function to connect Python with PostgreSQL
from datetime import datetime  # Import datetime to get current date and time

print("Reading parquet file...")  #display msg

df = pd.read_parquet(             #to read data
    "data/raw/yellow_tripdata_2024-01.parquet"
)

# to print total number of rows 
print("Rows:", len(df))

# Select required columns
df = df[
    [
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount"
    ]
]

# Rename columns
df = df.rename(
    columns={
        "VendorID": "vendor_id",
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime"
    }
)

# Metadata columns
#add new column to store the source filename
df["source_file"] = "yellow_tripdata_2024-01.parquet"

#add batch number to identify data load
df["batch_id"] = 1

#add current data and time when data is loaded
df["load_timestamp"] = datetime.now()

print(df.head())         #displays first 5 rows to verify data

# PostgreSQL connection
engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/uber_dw"
)

print("Loading data into PostgreSQL...")  #display msg

df.to_sql(
    name="trip_raw",  #
    schema="bronze",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

# Display success message after data is loaded
print("Data loaded successfully!")