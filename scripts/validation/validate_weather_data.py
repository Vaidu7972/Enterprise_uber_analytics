import pandas as pd
from utils.db_connection import get_engine

engine = get_engine()

df = pd.read_sql("SELECT * FROM bronze.weather_raw", engine)

print("Weather Data Validation")
print("Total Records:", len(df))
print("Null Weather Dates:", df["weather_date"].isnull().sum())
print("Duplicate Weather Dates:", df.duplicated(subset=["weather_date"]).sum())
print("Invalid Humidity:", len(df[(df["humidity"] < 0) | (df["humidity"] > 100)]))
print("Invalid Temperature:", len(df[(df["temperature"] < -50) | (df["temperature"] > 60)]))

print("Weather validation completed")