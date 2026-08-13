import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine
from utils.audit_logger import start_batch_log, update_batch_success, update_batch_failure

engine = get_engine()

PIPELINE_NAME = "enterprise_uber_analytics"
TASK_NAME = "load_dim_date"
SOURCE_NAME = "silver.trip_clean"
TARGET_TABLE = "gold.dim_date"

batch_id = start_batch_log(PIPELINE_NAME, TASK_NAME, SOURCE_NAME, TARGET_TABLE)

try:
    print("Reading dates from silver.trip_clean...")
    dates = pd.read_sql(
        text("""
            SELECT DISTINCT
                DATE(pickup_datetime) AS date_key
            FROM silver.trip_clean
            WHERE pickup_datetime IS NOT NULL
            ORDER BY DATE(pickup_datetime)
        """),
        engine,
    )

    rows_read = len(dates)
    print(f"Dates found: {rows_read}")

    if dates.empty:
        update_batch_success(
            batch_id=batch_id,
            rows_read=0,
            rows_inserted=0,
            rows_updated=0,
            rows_rejected=0,
        )
    else:
        dates["date_key"] = pd.to_datetime(dates["date_key"], errors="coerce")
        dates["day"] = dates["date_key"].dt.day
        dates["month"] = dates["date_key"].dt.month
        dates["year"] = dates["date_key"].dt.year
        dates["weekday"] = dates["date_key"].dt.day_name()
        dates["week_number"] = dates["date_key"].dt.isocalendar().week.astype(int)
        dates["quarter"] = dates["date_key"].dt.quarter
        dates["is_weekend"] = dates["weekday"].isin(["Saturday", "Sunday"])
        dates["date_key"] = dates["date_key"].dt.date
        dates = dates.drop_duplicates(subset=["date_key"]).copy()

        rows_inserted = 0
        with engine.begin() as conn:
            for _, row in dates.iterrows():
                result = conn.execute(
                    text("""
                        INSERT INTO gold.dim_date
                        (date_key, day, month, year, weekday, week_number, quarter, is_weekend)
                        VALUES
                        (:date_key, :day, :month, :year, :weekday, :week_number, :quarter, :is_weekend)
                        ON CONFLICT (date_key) DO NOTHING;
                    """),
                    {
                        "date_key": row["date_key"],
                        "day": int(row["day"]),
                        "month": int(row["month"]),
                        "year": int(row["year"]),
                        "weekday": str(row["weekday"]),
                        "week_number": int(row["week_number"]),
                        "quarter": int(row["quarter"]),
                        "is_weekend": bool(row["is_weekend"]),
                    },
                )
                rows_inserted += result.rowcount

        print("Date Dimension Loaded Successfully!")
        print(f"New dates inserted: {rows_inserted}")

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