
-- ===========================================================
-- ENTERPRISE UBER ANALYTICS DATABASE SETUP
-- Run this inside uber_dw database
-- ===========================================================

-- ===========================================================
-- CREATE SCHEMAS
-- ===========================================================

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- ===========================================================
-- BRONZE LAYER TABLES
-- ===========================================================

DROP TABLE IF EXISTS bronze.trip_raw CASCADE;
DROP TABLE IF EXISTS bronze.driver_raw CASCADE;
DROP TABLE IF EXISTS bronze.customer_raw CASCADE;
DROP TABLE IF EXISTS bronze.weather_raw CASCADE;

CREATE TABLE bronze.trip_raw
(
    trip_id BIGSERIAL PRIMARY KEY,
    vendor_id VARCHAR(50),
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance NUMERIC(10,2),
    fare_amount NUMERIC(10,2),
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bronze.driver_raw
(
    driver_id VARCHAR(50),
    driver_name VARCHAR(200),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    join_date DATE,
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bronze.customer_raw
(
    customer_id VARCHAR(50),
    customer_name VARCHAR(200),
    gender VARCHAR(20),
    city VARCHAR(100),
    signup_date DATE,
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bronze.weather_raw
(
    weather_date DATE,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    rainfall NUMERIC(5,2),
    wind_speed NUMERIC(5,2),
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================================
-- SILVER LAYER TABLES
-- ===========================================================

DROP TABLE IF EXISTS silver.trip_enriched CASCADE;
DROP TABLE IF EXISTS silver.trip_clean CASCADE;
DROP TABLE IF EXISTS silver.trip_rejected CASCADE;
DROP TABLE IF EXISTS silver.driver_clean CASCADE;
DROP TABLE IF EXISTS silver.customer_clean CASCADE;
DROP TABLE IF EXISTS silver.weather_clean CASCADE;

CREATE TABLE silver.trip_clean
(
    trip_id BIGINT PRIMARY KEY,
    vendor_id VARCHAR(50),
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance NUMERIC(10,2),
    fare_amount NUMERIC(10,2),
    trip_duration_minutes NUMERIC(10,2),
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP,
    cleaned_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE silver.trip_rejected
(
    trip_id BIGINT,
    vendor_id VARCHAR(50),
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance NUMERIC(10,2),
    fare_amount NUMERIC(10,2),
    rejection_reason VARCHAR(255),
    rejected_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE silver.driver_clean
(
    driver_id VARCHAR(50) PRIMARY KEY,
    driver_name VARCHAR(200),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    join_date DATE,
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP,
    cleaned_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE silver.customer_clean
(
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(200),
    gender VARCHAR(20),
    city VARCHAR(100),
    signup_date DATE,
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP,
    cleaned_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE silver.weather_clean
(
    weather_date DATE PRIMARY KEY,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    rainfall NUMERIC(5,2),
    wind_speed NUMERIC(5,2),
    source_file VARCHAR(255),
    batch_id INT,
    load_timestamp TIMESTAMP,
    cleaned_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE silver.trip_enriched
(
    trip_id BIGINT PRIMARY KEY,
    vendor_id VARCHAR(50),
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance NUMERIC(10,2),
    fare_amount NUMERIC(10,2),
    trip_duration_minutes NUMERIC(10,2),

    driver_id VARCHAR(50),
    driver_name VARCHAR(200),
    driver_rating NUMERIC(3,2),
    driver_city VARCHAR(100),

    customer_id VARCHAR(50),
    customer_name VARCHAR(200),
    customer_city VARCHAR(100),

    weather_date DATE,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),

    load_timestamp TIMESTAMP
);

-- ===========================================================
-- GOLD LAYER TABLES
-- ===========================================================

DROP TABLE IF EXISTS gold.fact_trip CASCADE;
DROP TABLE IF EXISTS gold.dim_driver CASCADE;
DROP TABLE IF EXISTS gold.dim_customer CASCADE;
DROP TABLE IF EXISTS gold.dim_weather CASCADE;
DROP TABLE IF EXISTS gold.dim_date CASCADE;

CREATE TABLE gold.dim_driver
(
    driver_key SERIAL PRIMARY KEY,
    driver_id VARCHAR(50) UNIQUE NOT NULL,
    driver_name VARCHAR(200),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

CREATE TABLE gold.dim_customer
(
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    city VARCHAR(100),
    gender VARCHAR(20),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

CREATE TABLE gold.dim_weather
(
    weather_key SERIAL PRIMARY KEY,
    weather_date DATE UNIQUE NOT NULL,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    rainfall NUMERIC(5,2),
    wind_speed NUMERIC(5,2)
);

CREATE TABLE gold.dim_date
(
    date_key DATE PRIMARY KEY,
    day INT,
    month INT,
    year INT,
    weekday VARCHAR(20),
    week_number INT,
    quarter INT,
    is_weekend BOOLEAN
);

CREATE TABLE gold.fact_trip
(
    trip_id BIGINT PRIMARY KEY,
    driver_key INT NOT NULL,
    customer_key INT NOT NULL,
    weather_key INT,
    date_key DATE NOT NULL,
    fare_amount NUMERIC(10,2),
    trip_distance NUMERIC(10,2),
    trip_duration_minutes NUMERIC(10,2),
    passenger_count INT,

    CONSTRAINT fk_driver
        FOREIGN KEY(driver_key)
        REFERENCES gold.dim_driver(driver_key),

    CONSTRAINT fk_customer
        FOREIGN KEY(customer_key)
        REFERENCES gold.dim_customer(customer_key),

    CONSTRAINT fk_weather
        FOREIGN KEY(weather_key)
        REFERENCES gold.dim_weather(weather_key),

    CONSTRAINT fk_date
        FOREIGN KEY(date_key)
        REFERENCES gold.dim_date(date_key)
);

-- ===========================================================
-- ANALYTICS MART TABLES
-- ===========================================================

DROP TABLE IF EXISTS gold.kpi_summary CASCADE;
DROP TABLE IF EXISTS gold.revenue_mart CASCADE;
DROP TABLE IF EXISTS gold.driver_performance_mart CASCADE;

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

-- ===========================================================
-- VERIFY CREATED TABLES
-- ===========================================================

SELECT 
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema IN ('bronze', 'silver', 'gold')
ORDER BY table_schema, table_name;

SELECT COUNT(*) FROM bronze.trip_raw;        --2964624
SELECT COUNT(*) FROM bronze.driver_raw;      --5000
SELECT COUNT(*) FROM bronze.customer_raw;    --5000
SELECT COUNT(*) FROM bronze.weather_raw;     --366

SELECT COUNT(*) FROM silver.trip_clean;      --9492
SELECT COUNT(*) FROM silver.trip_rejected;   --508
SELECT COUNT(*) FROM silver.driver_clean;    --5000
SELECT COUNT(*) FROM silver.customer_clean;  --5000
SELECT COUNT(*) FROM silver.weather_clean;   --366
SELECT COUNT(*) FROM silver.trip_enriched;   --0

SHOW port;
SELECT current_database(), current_user;
ALTER USER postgres WITH PASSWORD 'root';
SELECT 'Password reset done' AS status;

SELECT COUNT(*) FROM silver.trip_enriched;
SELECT * FROM silver.trip_enriched LIMIT 5;

SELECT COUNT(*) FROM gold.dim_driver;
SELECT COUNT(*) FROM gold.dim_customer;
SELECT COUNT(*) FROM gold.dim_weather;
SELECT COUNT(*) FROM gold.dim_date;

SELECT 
    DATE(pickup_datetime) AS trip_date,
    COUNT(*) AS total_trips
FROM silver.trip_clean
GROUP BY DATE(pickup_datetime)
ORDER BY trip_date;

TRUNCATE TABLE silver.trip_clean CASCADE;
TRUNCATE TABLE silver.trip_rejected CASCADE;
TRUNCATE TABLE silver.trip_enriched CASCADE;

TRUNCATE TABLE gold.fact_trip RESTART IDENTITY CASCADE;
TRUNCATE TABLE gold.dim_driver RESTART IDENTITY CASCADE;
TRUNCATE TABLE gold.dim_customer RESTART IDENTITY CASCADE;
TRUNCATE TABLE gold.dim_weather RESTART IDENTITY CASCADE;
TRUNCATE TABLE gold.dim_date CASCADE;

TRUNCATE TABLE gold.kpi_summary;
TRUNCATE TABLE gold.revenue_mart;
TRUNCATE TABLE gold.driver_performance_mart;

SELECT 
    DATE(pickup_datetime) AS trip_date,
    COUNT(*) AS total_trips
FROM silver.trip_clean
GROUP BY DATE(pickup_datetime)
ORDER BY trip_date;

SELECT 
    date_key,
    total_trips,
    total_revenue
FROM gold.revenue_mart
ORDER BY date_key;

SELECT 
    date_key,
    total_trips,
    total_revenue
FROM gold.revenue_mart
ORDER BY date_key;

--Final verification
SELECT 'silver.trip_clean' AS table_name, COUNT(*) FROM silver.trip_clean
UNION ALL
SELECT 'silver.trip_enriched', COUNT(*) FROM silver.trip_enriched
UNION ALL
SELECT 'gold.dim_driver', COUNT(*) FROM gold.dim_driver
UNION ALL
SELECT 'gold.dim_customer', COUNT(*) FROM gold.dim_customer
UNION ALL
SELECT 'gold.dim_weather', COUNT(*) FROM gold.dim_weather
UNION ALL
SELECT 'gold.dim_date', COUNT(*) FROM gold.dim_date
UNION ALL
SELECT 'gold.fact_trip', COUNT(*) FROM gold.fact_trip
UNION ALL
SELECT 'gold.revenue_mart', COUNT(*) FROM gold.revenue_mart
UNION ALL
SELECT 'gold.driver_performance_mart', COUNT(*) FROM gold.driver_performance_mart;

SELECT 
    date_key,
    total_trips,
    total_revenue
FROM gold.revenue_mart
ORDER BY date_key;