import pandas as pd

def generate_business_insights(data_result: dict = None, ml_result: dict = None, support_result: dict = None): #none - default -> dict
    """
    Insight Engine: Compute deterministic metric summaries and analytical insights
    across Data, ML, and Support Policy evidence.
    """
    insights = []     #empty containers
    kpis = {}

    # Data Agent Insight Extraction
    #1. data agent result exist , 2. dataframe --> pandas , 3. Dataframe non empty 
    if data_result and isinstance(data_result.get("data"), pd.DataFrame) and not data_result["data"].empty:
        df = data_result["data"]                #store
        kpis["record_count"] = len(df)          #count record

        #detect numerical column(id , rating , total trips)

        num_cols = df.select_dtypes(include="number").columns.tolist()   #pandas column to python list     
        if num_cols:
            for col in num_cols[:3]:      #atmost 3 
                kpis[f"total_{col}"] = float(df[col].sum())
                kpis[f"avg_{col}"] = round(float(df[col].mean()), 2)

        insights.append(f"Warehouse query returned {len(df)} records.")
        if "total_revenue" in df.columns:
            total_rev = df["total_revenue"].sum()
            insights.append(f"Total calculated revenue across query scope: ${total_rev:,.2f}")

    # ML Agent Insight Extraction
    if ml_result and "predictions" in ml_result:
        preds = ml_result["predictions"]
        if preds.get("mode") == "batch":
            high_count = preds.get("high_risk_count", 0)
            total = preds.get("total_drivers_scored", 1)
            pct = round((high_count / total) * 100, 1)
            insights.append(f"Predictive ML scored {total} drivers: {high_count} ({pct}%) flagged as High Underperformance Risk.")
            kpis["high_risk_driver_count"] = high_count
        elif preds.get("found"):
            risk_lvl = preds.get("risk_level")
            prob = preds.get("risk_probability", 0) * 100
            d_name = preds.get("driver_name", preds.get("driver_id"))
            rating = preds.get("rating")
            insights.append(f"ML Model evaluated Driver {d_name}: {risk_lvl} Risk ({prob:.1f}% probability) driven by rating of {rating}.")
            kpis["driver_risk_probability"] = prob

    # Support Policy Insight Extraction
    if support_result and support_result.get("sources"):
        sources = [f"{s['source']} (p.{s['page']})" for s in support_result["sources"]]
        insights.append(f"Grounded policy guidance retrieved from {len(sources)} support documents: {', '.join(sources)}.")

    return {
        "insight_summary": "\n".join([f"• {i}" for i in insights]) if insights else "No quantitative insights generated.",
        "insights_list": insights,
        "kpis": kpis
    }
