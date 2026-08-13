import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

def get_driver_features() -> pd.DataFrame:
    """
    Extract driver metrics from PostgreSQL Gold warehouse for feature engineering.
    """
    query = text("""
        SELECT 
            d.driver_id,
            d.driver_name,
            d.city,
            COALESCE(d.rating, 4.5) AS rating,
            COUNT(f.trip_id) AS total_trips,
            COALESCE(SUM(f.fare_amount), 0) AS total_revenue,
            COALESCE(AVG(f.fare_amount), 0) AS average_fare,
            COALESCE(AVG(f.trip_distance), 0) AS average_distance,
            COALESCE(AVG(f.trip_duration_minutes), 0) AS average_duration
        FROM gold.dim_driver d
        LEFT JOIN gold.fact_trip f ON d.driver_key = f.driver_key
        GROUP BY d.driver_id, d.driver_name, d.city, d.rating
        ORDER BY d.driver_id;
    """)

    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    # Derived features & target label logic
    # Objective threshold: Rating < 4.5 or Total Trips < 15 or Average Fare < 30
    df["rating"] = df["rating"].astype(float)
    df["total_trips"] = df["total_trips"].astype(int)
    df["total_revenue"] = df["total_revenue"].astype(float)
    df["average_fare"] = df["average_fare"].astype(float)
    df["average_distance"] = df["average_distance"].astype(float)
    df["average_duration"] = df["average_duration"].astype(float)

    # Documented target label based on rating percentile threshold:
    # Drivers with rating below median (50th percentile) are flagged as underperformance risk (1), rest (0).
    median_rating = float(df["rating"].median())
    df["underperformance_risk"] = (df["rating"] < median_rating).astype(int)

    return df


