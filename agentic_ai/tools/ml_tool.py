import json
import joblib
import pandas as pd
from agentic_ai.config.agent_config import MODEL_FILE_PATH, MODEL_META_PATH
from agentic_ai.ml.feature_engineering import get_driver_features


def predict_driver_risk(driver_id: str = None) -> dict:
    """
    Load the trained driver underperformance model and perform predictions.
    If driver_id is specified, score that specific driver.
    If driver_id is None, score all drivers and return top high-risk drivers.
    """
    if not MODEL_FILE_PATH.exists():
        raise RuntimeError("ML model file not found. Train the model first.")

    model = joblib.load(MODEL_FILE_PATH)

    meta = {}
    if MODEL_META_PATH.exists():
        with open(MODEL_META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

    feature_cols = meta.get("features", [
        "rating", "total_trips", "total_revenue", 
        "average_fare", "average_distance", "average_duration"
    ])

    df = get_driver_features()
    if df.empty:
        return {"error": "No driver data available."}

    # Execute predictions
    X = df[feature_cols]
    probabilities = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)

    df["risk_probability"] = probabilities
    df["risk_level"] = df["risk_probability"].apply(
        lambda p: "High" if p >= 0.65 else ("Medium" if p >= 0.35 else "Low")
    )

    if driver_id:
        driver_id_clean = str(driver_id).strip().upper()
        match = df[df["driver_id"].str.upper() == driver_id_clean]
        
        if match.empty:
            # Fallback: check if user passed numbers like D101 vs 101
            match = df[df["driver_id"].str.contains(driver_id_clean, case=False)]

        if match.empty:
            return {
                "found": False,
                "driver_id": driver_id,
                "message": f"Driver {driver_id} was not found in the Gold warehouse.",
                "all_high_risk_drivers": df[df["risk_level"] == "High"][["driver_id", "driver_name", "risk_probability", "risk_level"]].to_dict(orient="records")
            }

        row = match.iloc[0]
        return {
            "found": True,
            "driver_id": row["driver_id"],
            "driver_name": row["driver_name"],
            "city": row["city"],
            "rating": float(row["rating"]),
            "total_trips": int(row["total_trips"]),
            "total_revenue": float(row["total_revenue"]),
            "average_fare": float(row["average_fare"]),
            "risk_probability": round(float(row["risk_probability"]), 4),
            "risk_level": row["risk_level"],
            "features_used": {col: float(row[col]) for col in feature_cols},
            "model_info": meta
        }

    # Summary of all drivers sorted by risk probability descending
    high_risk_list = df.sort_values(by="risk_probability", ascending=False).head(10)
    
    return {
        "found": True,
        "mode": "batch",
        "total_drivers_scored": len(df),
        "high_risk_count": int((df["risk_level"] == "High").sum()),
        "medium_risk_count": int((df["risk_level"] == "Medium").sum()),
        "low_risk_count": int((df["risk_level"] == "Low").sum()),
        "top_high_risk_drivers": high_risk_list[["driver_id", "driver_name", "city", "rating", "total_trips", "average_fare", "risk_probability", "risk_level"]].to_dict(orient="records"),
        "model_info": meta
    }
