-- ===========================================================
-- ANALYTICS MART TABLES
-- Enterprise Uber Analytics Data Platform
-- ===========================================================

DROP TABLE IF EXISTS gold.kpi_summary;
DROP TABLE IF EXISTS gold.revenue_mart;
DROP TABLE IF EXISTS gold.driver_performance_mart;

-- KPI Summary Table
CREATE TABLE gold.kpi_summary
(
    total_trips BIGINT,
    total_revenue NUMERIC(12,2),
    average_fare NUMERIC(10,2),
    average_distance NUMERIC(10,2),
    average_trip_duration NUMERIC(10,2),
    average_passenger_count NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revenue Mart
CREATE TABLE gold.revenue_mart
(
    date_key DATE,
    year INT,
    month INT,
    weekday VARCHAR(20),
    is_weekend BOOLEAN,
    total_trips BIGINT,
    total_revenue NUMERIC(12,2),
    average_fare NUMERIC(10,2),
    average_distance NUMERIC(10,2)
);

-- Driver Performance Mart
CREATE TABLE gold.driver_performance_mart
(
    driver_key INT,
    driver_id VARCHAR(50),
    driver_name VARCHAR(200),
    driver_city VARCHAR(100),
    driver_rating NUMERIC(3,2),
    total_trips BIGINT,
    total_revenue NUMERIC(12,2),
    average_fare NUMERIC(10,2),
    average_distance NUMERIC(10,2),
    average_trip_duration NUMERIC(10,2)
);

SELECT 'Analytics Mart Tables Created Successfully!' AS status;