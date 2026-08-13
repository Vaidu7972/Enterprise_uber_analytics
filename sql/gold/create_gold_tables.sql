-- ===========================================
-- Gold Schema & Enterprise Uber Analytics Data Platform
-- ===========================================

CREATE SCHEMA IF NOT EXISTS gold;

--------------------------------------------------------------
-- Drop Existing Tables
--------------------------------------------------------------

DROP TABLE IF EXISTS gold.fact_trip CASCADE;
DROP TABLE IF EXISTS gold.dim_driver CASCADE;
DROP TABLE IF EXISTS gold.dim_customer CASCADE;
DROP TABLE IF EXISTS gold.dim_weather CASCADE;
DROP TABLE IF EXISTS gold.dim_date CASCADE;

--------------------------------------------------------------
-- Driver Dimension (SCD Type 2: Multiple rows per driver_id)
--------------------------------------------------------------

CREATE TABLE gold.dim_driver
(
    driver_key SERIAL PRIMARY KEY,
    driver_id VARCHAR(50) NOT NULL,
    driver_name VARCHAR(200),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

--------------------------------------------------------------
-- Customer Dimension (SCD Type 1 + SCD Type 3: previous_city & city_change_date)
--------------------------------------------------------------

CREATE TABLE gold.dim_customer
(
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    city VARCHAR(100),
    gender VARCHAR(20),
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN,
    previous_city VARCHAR(100),
    city_change_date DATE
);

--------------------------------------------------------------
-- Weather Dimension
--------------------------------------------------------------

CREATE TABLE gold.dim_weather
(
    weather_key SERIAL PRIMARY KEY,
    weather_date DATE UNIQUE NOT NULL,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    rainfall NUMERIC(5,2),
    wind_speed NUMERIC(5,2)
);

--------------------------------------------------------------
-- Date Dimension
--------------------------------------------------------------

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

--------------------------------------------------------------
-- Fact Trip
--------------------------------------------------------------

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

--------------------------------------------------------------
-- Success Message
--------------------------------------------------------------

SELECT 'Gold Layer Tables Created Successfully!' AS Status;