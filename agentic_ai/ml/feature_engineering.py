import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

def get_driver_features() -> pd.DataFrame:
    """
    Extract driver metrics from PostgreSQL Gold warehouse using temporal split.
    Period 1 (Jan 1 - Jan 20): Used exclusively for historical input features.
    Period 2 (Jan 21 - Jan 31): Used exclusively to construct the future target label.
    This eliminates target leakage (e.g. using current rating to define target while including rating as a feature).
    """
    query = text("""
        SELECT 
            d.driver_id,
            d.driver_name,
            d.city,
            COALESCE(d.rating, 4.5) AS rating,
            COUNT(CASE WHEN f.date_key BETWEEN '2024-01-01' AND '2024-01-20' THEN f.trip_id END) AS total_trips,
            COALESCE(SUM(CASE WHEN f.date_key BETWEEN '2024-01-01' AND '2024-01-20' THEN f.fare_amount END), 0) AS total_revenue,
            COALESCE(AVG(CASE WHEN f.date_key BETWEEN '2024-01-01' AND '2024-01-20' THEN f.fare_amount END), 0) AS average_fare,
            COALESCE(AVG(CASE WHEN f.date_key BETWEEN '2024-01-01' AND '2024-01-20' THEN f.trip_distance END), 0) AS average_distance,
            COALESCE(AVG(CASE WHEN f.date_key BETWEEN '2024-01-01' AND '2024-01-20' THEN f.trip_duration_minutes END), 0) AS average_duration,
            COALESCE(SUM(CASE WHEN f.date_key BETWEEN '2024-01-21' AND '2024-01-31' THEN f.fare_amount END), 0) AS future_revenue,
            COUNT(CASE WHEN f.date_key BETWEEN '2024-01-21' AND '2024-01-31' THEN f.trip_id END) AS future_trips
        FROM gold.dim_driver d
        LEFT JOIN gold.fact_trip f ON d.driver_key = f.driver_key
        GROUP BY d.driver_id, d.driver_name, d.city, d.rating
        ORDER BY d.driver_id;
    """)

    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    df["rating"] = df["rating"].astype(float)
    df["total_trips"] = df["total_trips"].astype(int)
    df["total_revenue"] = df["total_revenue"].astype(float)
    df["average_fare"] = df["average_fare"].astype(float)
    df["average_distance"] = df["average_distance"].astype(float)
    df["average_duration"] = df["average_duration"].astype(float)
    df["future_revenue"] = df["future_revenue"].astype(float)
    df["future_trips"] = df["future_trips"].astype(int)

    # Target label: Non-leaky future underperformance defined by Period 2 revenue & trip volume
    # Target = 1 if Period 2 future revenue is in bottom 35th percentile or future trips < 1
    p35_future_rev = float(df["future_revenue"].quantile(0.35))
    df["underperformance_risk"] = ((df["future_revenue"] <= p35_future_rev) | (df["future_trips"] < 1)).astype(int)

    return df


