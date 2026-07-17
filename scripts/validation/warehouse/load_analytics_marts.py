from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Starting Analytics Mart Load...")

with engine.begin() as conn:

    print("Clearing old mart data...")

    conn.execute(text("TRUNCATE TABLE gold.kpi_summary;"))
    conn.execute(text("TRUNCATE TABLE gold.revenue_mart;"))
    conn.execute(text("TRUNCATE TABLE gold.driver_performance_mart;"))

    print("Loading KPI Summary...")

    conn.execute(text("""
        INSERT INTO gold.kpi_summary
        (
            total_trips,
            total_revenue,
            average_fare,
            average_distance,
            average_trip_duration,
            average_passenger_count
        )
        SELECT
            COUNT(*) AS total_trips,
            ROUND(SUM(fare_amount), 2) AS total_revenue,
            ROUND(AVG(fare_amount), 2) AS average_fare,
            ROUND(AVG(trip_distance), 2) AS average_distance,
            ROUND(AVG(trip_duration_minutes), 2) AS average_trip_duration,
            ROUND(AVG(passenger_count), 2) AS average_passenger_count
        FROM gold.fact_trip;
    """))

    print("Loading Revenue Mart...")

    conn.execute(text("""
        INSERT INTO gold.revenue_mart
        (
            date_key,
            year,
            month,
            weekday,
            is_weekend,
            total_trips,
            total_revenue,
            average_fare,
            average_distance
        )
        SELECT
            d.date_key,
            d.year,
            d.month,
            d.weekday,
            d.is_weekend,
            COUNT(f.trip_id) AS total_trips,
            ROUND(SUM(f.fare_amount), 2) AS total_revenue,
            ROUND(AVG(f.fare_amount), 2) AS average_fare,
            ROUND(AVG(f.trip_distance), 2) AS average_distance
        FROM gold.fact_trip f
        JOIN gold.dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            d.date_key,
            d.year,
            d.month,
            d.weekday,
            d.is_weekend
        ORDER BY d.date_key;
    """))

    print("Loading Driver Performance Mart...")

    conn.execute(text("""
        INSERT INTO gold.driver_performance_mart
        (
            driver_key,
            driver_id,
            driver_name,
            driver_city,
            driver_rating,
            total_trips,
            total_revenue,
            average_fare,
            average_distance,
            average_trip_duration
        )
        SELECT
            d.driver_key,
            d.driver_id,
            d.driver_name,
            d.city AS driver_city,
            d.rating AS driver_rating,
            COUNT(f.trip_id) AS total_trips,
            ROUND(SUM(f.fare_amount), 2) AS total_revenue,
            ROUND(AVG(f.fare_amount), 2) AS average_fare,
            ROUND(AVG(f.trip_distance), 2) AS average_distance,
            ROUND(AVG(f.trip_duration_minutes), 2) AS average_trip_duration
        FROM gold.fact_trip f
        JOIN gold.dim_driver d
            ON f.driver_key = d.driver_key
        GROUP BY
            d.driver_key,
            d.driver_id,
            d.driver_name,
            d.city,
            d.rating
        ORDER BY total_revenue DESC;
    """))

print("Analytics Mart Load Completed Successfully!")