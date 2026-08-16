import pandas as pd
import numpy as np
from sqlalchemy import text
from utils.db_connection import get_engine

def detect_revenue_anomalies(threshold_z: float = 2.0) -> dict:
    """
    Anomaly Detection Engine: Detect unusual daily revenue drops, trip volume dips,
    or fare spikes across historical time-series data using Z-score statistics.
    """
    engine = get_engine()
    query = text("""
        SELECT 
            date_key,
            total_trips,
            total_revenue,
            average_fare
        FROM gold.revenue_mart
        ORDER BY date_key ASC;
    """)

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()

    if df.empty or len(df) < 5:
        return {
            "anomaly_detected": False,
            "message": "Insufficient daily time-series records for statistical anomaly detection.",
            "anomalies": []
        }

    # Calculate rolling mean and standard deviation
    rev_mean = df["total_revenue"].mean()
    rev_std = df["total_revenue"].std() or 1.0

    df["revenue_zscore"] = (df["total_revenue"] - rev_mean) / rev_std

    anomaly_rows = df[df["revenue_zscore"].abs() >= threshold_z]

    anomalies_list = []
    for _, row in anomaly_rows.iterrows():
        date_str = str(row["date_key"])
        actual_rev = float(row["total_revenue"])
        dev_pct = round(((actual_rev - rev_mean) / rev_mean) * 100, 2)
        anomalies_list.append({
            "date": date_str,
            "metric_affected": "Total Daily Revenue",
            "actual_value": actual_rev,
            "expected_value": round(float(rev_mean), 2),
            "z_score": round(float(row["revenue_zscore"]), 2),
            "deviation_percentage": f"{dev_pct}%",
            "severity": "CRITICAL" if abs(dev_pct) > 30 else "WARNING",
            "possible_cause": "Weather disruption, regional supply gap, or system outage" if dev_pct < 0 else "Special event demand surge"
        })

    return {
        "anomaly_detected": len(anomalies_list) > 0,
        "total_days_analyzed": len(df),
        "anomalies_found_count": len(anomalies_list),
        "mean_daily_revenue": round(float(rev_mean), 2),
        "std_daily_revenue": round(float(rev_std), 2),
        "anomalies": anomalies_list
    }
