-- ===========================================
-- Gold Schema
-- ===========================================

CREATE SCHEMA IF NOT EXISTS gold;

-- Driver Dimension
CREATE TABLE IF NOT EXISTS gold.dim_driver
(
    driver_key SERIAL PRIMARY KEY,
    driver_id VARCHAR(50),
    driver_name VARCHAR(200),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

-- Customer Dimension
CREATE TABLE IF NOT EXISTS gold.dim_customer
(
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50),
    customer_name VARCHAR(200),
    city VARCHAR(100),
    gender VARCHAR(20),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

-- Weather Dimension
CREATE TABLE IF NOT EXISTS gold.dim_weather
(
    weather_key SERIAL PRIMARY KEY,
    weather_date DATE,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    rainfall NUMERIC(5,2),
    wind_speed NUMERIC(5,2)
);

-- Date Dimension
CREATE TABLE IF NOT EXISTS gold.dim_date
(
    date_key DATE PRIMARY KEY,
    day INT,
    month INT,
    year INT,
    weekday VARCHAR(20),
    weekend BOOLEAN
);

-- Fact Trip
CREATE TABLE IF NOT EXISTS gold.fact_trip
(
    trip_id BIGINT PRIMARY KEY,

    driver_key INT,
    customer_key INT,
    weather_key INT,
    date_key DATE,

    fare_amount NUMERIC(10,2),
    trip_distance NUMERIC(10,2),
    trip_duration_minutes NUMERIC(10,2),
    passenger_count INT
);