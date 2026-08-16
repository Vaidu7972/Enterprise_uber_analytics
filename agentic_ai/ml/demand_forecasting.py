import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

def predict_demand(city: str = None, date_str: str = None, hour: int = 18) -> dict:
    """
    Demand Forecasting Tool: Predict expected trip volume, demand intensity level,
    expected revenue, and peak windows based on historical PostgreSQL Gold warehouse data.
    """
    engine = get_engine()
    query = text("""
        SELECT 
            d.weekday,
            d.is_weekend,
            dr.city,
            COUNT(f.trip_id) AS historical_trips,
            AVG(f.fare_amount) AS avg_fare,
            AVG(f.trip_distance) AS avg_distance,
            COALESCE(AVG(w.temperature), 72) AS avg_temp
        FROM gold.fact_trip f
        JOIN gold.dim_driver dr ON f.driver_key = dr.driver_key
        JOIN gold.dim_date d ON f.date_key = d.date_key
        LEFT JOIN gold.dim_weather w ON f.date_key = w.weather_date
        GROUP BY d.weekday, d.is_weekend, dr.city;
    """)

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        return {
            "success": False,
            "message": "Insufficient historical trip data to generate demand forecast.",
            "predicted_trips": 0,
            "demand_level": "Unknown"
        }

    if city:
        city_clean = city.strip().title()
        df_filtered = df[df["city"].str.title() == city_clean]
        if df_filtered.empty:
            df_filtered = df
    else:
        df_filtered = df

    avg_daily_trips = float(df_filtered["historical_trips"].mean())
    avg_fare = float(df_filtered["avg_fare"].mean())

    # Hourly multiplier & weekend factor
    peak_multiplier = 1.35 if hour in (8, 9, 17, 18, 19, 20) else 0.85
    predicted_trips = max(10, int(avg_daily_trips * peak_multiplier))
    predicted_revenue = round(predicted_trips * avg_fare, 2)

    if predicted_trips > avg_daily_trips * 1.2:
        demand_level = "HIGH DEMAND"
        recommendation = "Deploy peak surcharge incentive ($3.50/trip) to encourage driver availability in key zones."
    elif predicted_trips < avg_daily_trips * 0.8:
        demand_level = "LOW DEMAND"
        recommendation = "Consolidate driver distribution toward central transport hubs."
    else:
        demand_level = "MODERATE DEMAND"
        recommendation = "Standard fleet allocation optimal for projected trip volume."

    # Top high demand zones by historical volume
    city_summary = df.groupby("city")["historical_trips"].sum().reset_index()
    top_zones = city_summary.sort_values(by="historical_trips", ascending=False).head(3)["city"].tolist()

    return {
        "success": True,
        "city": city or "System Wide",
        "target_hour": f"{hour:02d}:00",
        "predicted_trips": predicted_trips,
        "predicted_revenue": predicted_revenue,
        "expected_avg_fare": round(avg_fare, 2),
        "demand_level": demand_level,
        "peak_window": "08:00 - 10:00 & 17:00 - 20:00",
        "high_demand_zones": top_zones if top_zones else ["Downtown", "Airport", "Midtown"],
        "recommendation": recommendation,
        "model_basis": "Historical trip volume aggregations from Gold warehouse."
    }
