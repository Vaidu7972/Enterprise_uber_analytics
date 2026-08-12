## Power BI Dashboard
Enterprise Uber Analytics Data Platform
Project Objective

Build an end-to-end Data Engineering pipeline using:

Python
PostgreSQL
Great Expectations
Airflow
Docker
Power BI

Following the Medallion Architecture:

Raw Sources
    ↓
Bronze Layer
    ↓
Data Quality
    ↓
Silver Layer
    ↓
Gold Layer
    ↓
Analytics Dashboard

## Completed Work
### Phase 1 - Project Setup
- Created project folder structure
- Initialized Git repository
- Configured Python virtual environment

### Phase 2 - Data Acquisition
- Downloaded NYC TLC Yellow Taxi dataset
- Added Taxi Zone lookup data

### Phase 3 - Data Warehouse Setup
- Installed PostgreSQL
- Created database: uber_dw
- Created schemas:
  - bronze
  - silver
  - gold

### Phase 4 - Bronze Layer Development

#### Trip Data
- Created bronze.trip_raw
- Loaded 2.69M NYC taxi trip records
- Added metadata columns:
  - source_file
  - batch_id
  - load_timestamp

#### Driver Data
- Generated synthetic driver dataset (JSON)
- Created bronze.driver_raw
- Loaded 5000 driver records

#### Customer Data
- Generated synthetic customer dataset (XML)
- Created bronze.customer_raw
- Loaded 5000 customer records

#### Weather Data
- Generated weather dataset (CSV)
- Created bronze.weather_raw
- Loaded 366 weather records

The project includes a Power BI dashboard connected to the PostgreSQL Gold Layer and Analytics Mart tables.

### Dashboard Pages

1. Executive Dashboard
   - Total Revenue
   - Total Trips
   - Average Fare
   - Average Distance
   - Average Trip Duration
   - Revenue Trend by Date
   - Weekend vs Weekday Trips
   - Top Drivers by Revenue

2. Revenue Analysis Dashboard
   - Daily Revenue Trend
   - Daily Trip Count
   - Weekend vs Weekday Revenue
   - Revenue by Weekday
   - Daily Revenue Summary

3. Driver Performance Dashboard
   - Total Drivers
   - Total Trips
   - Total Revenue
   - Average Driver Rating
   - Average Trip Duration
   - Top Drivers by Revenue
   - Trips by Driver
   - Driver Rating vs Revenue
   - Driver Performance Summary

### Data Source

The dashboard uses the following PostgreSQL tables:

- `gold.fact_trip`
- `gold.dim_driver`
- `gold.dim_customer`
- `gold.dim_weather`
- `gold.dim_date`
- `gold.revenue_mart`
- `gold.driver_performance_mart`

### Dashboard File

The Power BI dashboard file is available at:

`dashboards/Enterprise_Uber_Analytics_Dashboard.pbix`

## Project Summary

Enterprise Uber Analytics Data Platform is an end-to-end data engineering and analytics project built using Python, PostgreSQL, SQL, and Power BI.

The project follows Medallion Architecture with Bronze, Silver, and Gold layers. Raw Uber trip, driver, customer, and weather data are ingested into PostgreSQL, cleaned and transformed using Python, and modeled into fact and dimension tables for analytics.

Power BI dashboards were created to analyze executive KPIs, revenue trends, and driver performance.

## Dashboards

1. Executive Dashboard
2. Revenue Analysis Dashboard
3. Driver Performance Dashboard

## Tech Stack

- Python
- Pandas
- PostgreSQL
- SQL
- Power BI
- GitHub
- VS Code

## Architecture

Raw Data → Bronze Layer → Silver Layer → Gold Layer → Analytics Marts → Power BI Dashboard

        ↓
Python Ingestion Scripts
        ↓
PostgreSQL Bronze Layer
        ↓
Data Validation
        ↓
Silver Cleaned Layer
        ↓
Gold Star Schema
        ↓
Analytics Marts
        ↓
Power BI Dashboards

AIrflow and docker
Windows
↓
Docker Desktop
↓
Airflow containers
↓
Your Uber pipeline scripts
↓
PostgreSQL
↓
Power BI dashboards

Final architecture after Airflow + Docker

Raw Files
CSV / JSON / XML / Weather CSV
        ↓
Dockerized PostgreSQL
        ↓
Airflow DAG
        ↓
Bronze Ingestion
        ↓
Data Validation
        ↓
Silver Transformation
        ↓
Trip Enrichment
        ↓
Gold Dimension + Fact Load
        ↓
Analytics Marts
        ↓
Power BI Dashboards

## Airflow and Docker Orchestration

This project uses Docker and Apache Airflow to automate the complete Uber Analytics Data Pipeline.

The Airflow DAG performs:

1. Raw data ingestion into Bronze layer
2. Data cleaning and validation into Silver layer
3. Enriched trip creation
4. Gold dimension and fact table loading
5. Analytics mart creation for Power BI dashboards

### Airflow DAG

DAG Name:

`enterprise_uber_analytics_pipeline`

### Docker Services

- PostgreSQL project database
- Airflow metadata PostgreSQL database
- Airflow webserver
- Airflow scheduler

### Run Commands

```bash
docker compose build
docker compose up
docker compose  up -d         (to start)
docker compose  ps
docker compose down           (to shutdown)
