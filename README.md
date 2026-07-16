## Power BI Dashboard

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
