import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

df = pd.read_sql("SELECT * FROM bronze.driver_raw", engine)

print("Driver Data Validation")
print("Total Records:", len(df))
print("Null Driver IDs:", df["driver_id"].isnull().sum())
print("Duplicate Driver IDs:", df.duplicated(subset=["driver_id"]).sum())
print("Invalid Ratings:", len(df[(df["rating"] < 1) | (df["rating"] > 5)]))

print("Driver validation completed")