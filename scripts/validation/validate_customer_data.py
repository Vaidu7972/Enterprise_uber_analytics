import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

df = pd.read_sql("SELECT * FROM bronze.customer_raw", engine)

print("Customer Data Validation")
print("Total Records:", len(df))
print("Null Customer IDs:", df["customer_id"].isnull().sum())
print("Duplicate Customer IDs:", df.duplicated(subset=["customer_id"]).sum())
print("Null Customer Names:", df["customer_name"].isnull().sum())
print("Invalid Gender:", len(df[~df["gender"].isin(["Male", "Female"])]))

print("Customer validation completed")