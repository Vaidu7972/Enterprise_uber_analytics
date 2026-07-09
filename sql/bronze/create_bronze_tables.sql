-- ===========================================
-- Bronze Schema
-- ===========================================

CREATE SCHEMA IF NOT EXISTS bronze;

-- Trip Raw Table
CREATE TABLE IF NOT EXISTS bronze.trip_raw
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

-- Driver Raw Table
CREATE TABLE IF NOT EXISTS bronze.driver_raw
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

-- Customer Raw Table
CREATE TABLE IF NOT EXISTS bronze.customer_raw
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

-- Weather Raw Table
CREATE TABLE IF NOT EXISTS bronze.weather_raw
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