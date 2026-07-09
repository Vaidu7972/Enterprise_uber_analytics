import pandas as pd
from utils.db_connection import get_engine
from utils.logger import logger

engine = get_engine()

logger.info("Loading Driver Dimension...")

drivers = pd.read_sql("""
SELECT
driver_id,
driver_name,
city,
rating
FROM silver.driver_clean
""", engine)

drivers["effective_date"] = pd.Timestamp.today().date()
drivers["end_date"] = None
drivers["is_current"] = True

drivers.to_sql(
    "dim_driver",
    schema="gold",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Driver Dimension Loaded Successfully!")
print("Rows:", len(drivers))