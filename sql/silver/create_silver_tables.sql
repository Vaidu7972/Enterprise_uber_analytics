-- ===========================================
-- Silver Schema
-- ===========================================

CREATE SCHEMA IF NOT EXISTS silver;

-- Clean Trips
CREATE TABLE IF NOT EXISTS silver.trip_clean
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

-- Rejected Trips
CREATE TABLE IF NOT EXISTS silver.trip_rejected
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

-- Driver Clean
CREATE TABLE IF NOT EXISTS silver.driver_clean
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

-- Customer Clean
CREATE TABLE IF NOT EXISTS silver.customer_clean
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

-- Weather Clean
CREATE TABLE IF NOT EXISTS silver.weather_clean
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

-- Enriched Trips
CREATE TABLE IF NOT EXISTS silver.trip_enriched
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