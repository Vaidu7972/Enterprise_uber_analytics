import datetime
import json
import joblib
import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine

from agentic_ai.config.agent_config import MODEL_FILE_PATH, MODEL_META_PATH
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.ml.demand_forecasting import predict_demand
from agentic_ai.ml.anomaly_detection import detect_revenue_anomalies

from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import (
    render_risk_ring,
    render_bullet_comparison,
    render_bar_chart,
    render_horizontal_bar_chart,
    render_histogram,
    render_scatter_chart,
    render_anomaly_chart,
)


@st.cache_data(ttl=60)
def get_filter_options() -> dict:
    """Fetch distinct filter option lists directly from PostgreSQL Gold warehouse."""
    engine = get_engine()
    cities, weekdays, passenger_counts = [], [], []
    try:
        with engine.connect() as conn:
            c_res = conn.execute(text("SELECT DISTINCT city FROM gold.dim_driver WHERE city IS NOT NULL ORDER BY city;")).scalars().all()
            cities = list(c_res)
            
            w_res = conn.execute(text("SELECT DISTINCT weekday FROM gold.dim_date WHERE weekday IS NOT NULL ORDER BY weekday;")).scalars().all()
            weekdays = list(w_res)

            p_res = conn.execute(text("SELECT DISTINCT passenger_count FROM gold.fact_trip WHERE passenger_count IS NOT NULL ORDER BY passenger_count;")).scalars().all()
            passenger_counts = [int(p) for p in p_res if p is not None]
    except Exception:
        cities = ["Pune", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        passenger_counts = [1, 2, 3, 4, 5, 6]

    return {
        "cities": cities if cities else ["Pune", "Mumbai", "Delhi", "Bangalore"],
        "weekdays": weekdays if weekdays else ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "passenger_counts": passenger_counts if passenger_counts else [1, 2, 3, 4, 5, 6],
    }


def render_prediction_studio_page():
    """Render SaaS Prediction Studio — Manual Categorical Scenario Builder."""
    st.markdown("""
        <div class="page-header">
            <h1>Prediction Studio</h1>
            <p>Build custom mobility scenarios using real warehouse categories and generate data-backed predictions.</p>
        </div>
    """, unsafe_allow_html=True)

    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []

    filter_opts = get_filter_options()

    # Top Control: Prediction Type
    st.markdown(f"""<div class="filter-bar">{get_icon_svg('Sparkles', '#8B5CF6', 20)} <b>Select Prediction Scenario Mode</b></div>""", unsafe_allow_html=True)
    
    pred_type = st.selectbox(
        "PREDICTION TYPE",
        [
            "1. Driver Risk Prediction",
            "2. Demand Estimate",
            "3. Revenue Scenario Estimate",
            "4. Trip Volume Estimate",
            "5. Segment Performance Analysis",
            "6. Anomaly Scenario Analysis",
        ],
        key="ps_pred_type_sel"
    )

    st.divider()

    # =========================================================================
    # MODE 1: DRIVER RISK PREDICTION
    # =========================================================================
    if pred_type.startswith("1"):
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('BrainCircuit', '#F59E0B', 18)} Mode 1: Driver Underperformance Risk Assessment & What-If Simulation</div>""", unsafe_allow_html=True)
        
        mode_choice = st.radio("Driver Risk Sub-Mode", ["Existing Warehouse Driver", "Scenario / What-If Simulation"], horizontal=True, key="ps_drv_submode")
        
        df_drivers = execute_read_only_query("SELECT driver_id, driver_name, driver_city, driver_rating, total_revenue, total_trips, average_fare, average_distance, average_trip_duration FROM gold.driver_performance_mart ORDER BY total_revenue DESC;")

        if not df_drivers.empty:
            if mode_choice == "Existing Warehouse Driver":
                d_opts = df_drivers.apply(lambda r: f"{r['driver_id']} — {r['driver_name']} ({r['driver_city']})", axis=1).tolist()
                sel_drv_str = st.selectbox("Select Target Driver", d_opts, key="ps_drv_sel")
                sel_drv_id = sel_drv_str.split(" — ")[0]

                drv_row = df_drivers[df_drivers["driver_id"] == sel_drv_id].iloc[0]

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Driver Rating", f"{drv_row['driver_rating']:.2f}")
                with c2:
                    st.metric("Total Revenue", f"${float(drv_row['total_revenue']):,.2f}")
                with c3:
                    st.metric("Total Trips", f"{int(drv_row['total_trips']):,}")
                with c4:
                    st.metric("Avg Fare", f"${float(drv_row['average_fare']):,.2f}")

                if st.button("PREDICT DRIVER RISK", key="btn_predict_existing_risk", type="primary"):
                    res = predict_driver_risk(driver_id=sel_drv_id)
                    if res.get("found"):
                        prob = res.get("risk_probability", 0)
                        lvl = res.get("risk_level", "Low")
                        
                        r_col1, r_col2 = st.columns([1, 2])
                        with r_col1:
                            render_risk_ring(prob, risk_level=lvl, title="Model Risk Probability")
                        with r_col2:
                            st.markdown(f"### ML Assessment: {render_status_pill(lvl)}", unsafe_allow_html=True)
                            st.write(f"• **Model:** `RandomForestClassifier`")
                            st.write(f"• **Risk Probability:** `{prob*100:.1f}%`")
                            st.write(f"• **Features Used:** `{list(res.get('features_used', {}).keys())}`")
                            
                            fleet_avg_fare = df_drivers["average_fare"].mean()
                            render_bullet_comparison(float(drv_row["average_fare"]), fleet_avg_fare, label="Driver Avg Fare vs Fleet Average", unit="$")

                        # Log history
                        st.session_state.prediction_history.append({
                            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                            "prediction_type": "Driver Risk (Existing)",
                            "filters": f"Driver {sel_drv_id}",
                            "result": f"{prob*100:.1f}% {lvl}",
                            "method": "RandomForest"
                        })

            else:
                # WHAT-IF SIMULATION MODE
                st.info("💡 **What-If Analysis**: Adjust driver features manually to observe how model risk probability reacts. Inputs strictly match the trained RandomForest feature space.")
                
                w1, w2, w3 = st.columns(3)
                with w1:
                    w_rating = st.slider("Driver Rating", 1.0, 5.0, 4.2, step=0.1, key="wf_rating")
                    w_trips = st.number_input("Total Trips", min_value=0, max_value=1000, value=150, step=10, key="wf_trips")
                with w2:
                    w_revenue = st.number_input("Total Revenue ($)", min_value=0.0, max_value=50000.0, value=3500.0, step=100.0, key="wf_revenue")
                    w_fare = st.number_input("Average Fare ($)", min_value=1.0, max_value=200.0, value=23.5, step=1.0, key="wf_fare")
                with w3:
                    w_distance = st.number_input("Average Distance (mi)", min_value=0.1, max_value=50.0, value=4.5, step=0.5, key="wf_distance")
                    w_duration = st.number_input("Average Duration (min)", min_value=1.0, max_value=120.0, value=18.0, step=1.0, key="wf_duration")

                if st.button("RUN WHAT-IF PREDICTION", key="btn_run_whatif", type="primary"):
                    if not MODEL_FILE_PATH.exists():
                        st.error("Model file missing.")
                    else:
                        model = joblib.load(MODEL_FILE_PATH)
                        meta = {}
                        if MODEL_META_PATH.exists():
                            with open(MODEL_META_PATH, "r", encoding="utf-8") as f:
                                meta = json.load(f)

                        feature_cols = meta.get("features", ["rating", "total_trips", "total_revenue", "average_fare", "average_distance", "average_duration"])
                        
                        input_df = pd.DataFrame([{
                            "rating": float(w_rating),
                            "total_trips": int(w_trips),
                            "total_revenue": float(w_revenue),
                            "average_fare": float(w_fare),
                            "average_distance": float(w_distance),
                            "average_duration": float(w_duration),
                        }])[feature_cols]

                        prob = model.predict_proba(input_df)[0, 1] if hasattr(model, "predict_proba") else float(model.predict(input_df)[0])
                        lvl = "High" if prob >= 0.65 else ("Medium" if prob >= 0.35 else "Low")

                        wf_col1, wf_col2 = st.columns([1, 2])
                        with wf_col1:
                            render_risk_ring(prob, risk_level=lvl, title="Simulated Scenario Risk")
                        with wf_col2:
                            st.markdown(f"### What-If Result: {render_status_pill(lvl)}", unsafe_allow_html=True)
                            st.write(f"• **Simulated Probability:** `{prob*100:.1f}%`")
                            st.write(f"• **Model:** `RandomForestClassifier`")
                            st.caption("ℹ️ **Notice:** This is a simulated what-if scenario and does not modify warehouse data.")

                        st.session_state.prediction_history.append({
                            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                            "prediction_type": "Driver Risk (What-If)",
                            "filters": f"Rating={w_rating}, Trips={w_trips}, Rev=${w_revenue}",
                            "result": f"{prob*100:.1f}% {lvl}",
                            "method": "RandomForest Simulation"
                        })

    # =========================================================================
    # MODE 2: HISTORICAL DEMAND ESTIMATE
    # =========================================================================
    elif pred_type.startswith("2"):
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#3B82F6', 18)} Mode 2: Historical Demand Estimate</div>""", unsafe_allow_html=True)
        st.caption("ℹ️ **Model Basis:** Historical trip volume aggregations & hourly demand weights from Gold warehouse.")

        d1, d2, d3 = st.columns(3)
        with d1:
            sel_city = st.selectbox("Target City", ["All Cities"] + filter_opts["cities"], key="dem_city")
        with d2:
            sel_hour = st.slider("Target Hour (0-23)", 0, 23, 18, key="dem_hour")
        with d3:
            sel_weather = st.selectbox("Weather Condition Category", ["All Conditions", "Dry", "Rainy (>0mm)", "High Humidity (>=70%)"], key="dem_weather")

        if st.button("ESTIMATE DEMAND", key="btn_est_demand", type="primary"):
            city_param = None if sel_city == "All Cities" else sel_city
            res = predict_demand(city=city_param, hour=sel_hour)

            if res.get("success"):
                st.markdown(f"### Historical Demand Output: {render_status_pill(res['demand_level'])}", unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    render_kpi_card("Estimated Trips", f"{res['predicted_trips']}", "ChartColumn", f"Target Hour {sel_hour}:00", "#3B82F6")
                with m2:
                    render_kpi_card("Expected Revenue", f"${res['predicted_revenue']:,.2f}", "TrendingUp", f"Avg Fare ${res['expected_avg_fare']:.2f}", "#10B981")
                with m3:
                    render_kpi_card("High Demand Zones", f"{len(res['high_demand_zones'])} Zones", "Activity", "Top Density", "#F59E0B")

                st.info(f"**Operational Recommendation:** {res['recommendation']}")

                if res.get("high_demand_zones"):
                    z_df = pd.DataFrame([{"Zone": z, "Volume Weight": (idx+1)*15} for idx, z in enumerate(res["high_demand_zones"])])
                    render_horizontal_bar_chart(z_df, "Zone", "Volume Weight", color="#F59E0B", height=200, title="Zone Volume Weight")

                st.session_state.prediction_history.append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "prediction_type": "Historical Demand Estimate",
                    "filters": f"City={sel_city}, Hour={sel_hour}:00",
                    "result": f"{res['predicted_trips']} Trips ({res['demand_level']})",
                    "method": "Warehouse Aggregation"
                })

    # =========================================================================
    # MODE 3: REVENUE SCENARIO ESTIMATE
    # =========================================================================
    elif pred_type.startswith("3"):
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#10B981', 18)} Mode 3: Historical Revenue Scenario Estimate</div>""", unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            sel_city_rev = st.selectbox("Target City", ["All Cities"] + filter_opts["cities"], key="rev_scen_city")
            sel_day_rev = st.selectbox("Day Type", ["All Days", "Weekend Only", "Weekday Only"], key="rev_scen_day")
        with r2:
            sel_dist_band = st.selectbox("Trip Distance Band", ["All Distances", "Short (0-3 mi)", "Medium (3-7 mi)", "Long (7-15 mi)", "Very Long (15+ mi)"], key="rev_scen_dist")
            sel_pass_cnt = st.selectbox("Passenger Count", ["All Counts"] + filter_opts["passenger_counts"], key="rev_scen_pass")
        with r3:
            exp_trips = st.number_input("Expected Scenario Trips", min_value=1, max_value=5000, value=100, step=10, key="rev_scen_exp_trips")

        if st.button("CALCULATE REVENUE SCENARIO", key="btn_calc_rev_scen", type="primary"):
            sql_where = []
            if sel_city_rev != "All Cities":
                sql_where.append(f"d.city = '{sel_city_rev}'")
            if sel_day_rev == "Weekend Only":
                sql_where.append("dt.is_weekend = TRUE")
            elif sel_day_rev == "Weekday Only":
                sql_where.append("dt.is_weekend = FALSE")

            if "Short" in sel_dist_band:
                sql_where.append("f.trip_distance BETWEEN 0 AND 3")
            elif "Medium" in sel_dist_band:
                sql_where.append("f.trip_distance BETWEEN 3 AND 7")
            elif "Long" in sel_dist_band:
                sql_where.append("f.trip_distance BETWEEN 7 AND 15")
            elif "Very Long" in sel_dist_band:
                sql_where.append("f.trip_distance > 15")

            if sel_pass_cnt != "All Counts":
                sql_where.append(f"f.passenger_count = {sel_pass_cnt}")

            where_str = ("WHERE " + " AND ".join(sql_where)) if sql_where else ""

            query = f"""
                SELECT 
                    COUNT(f.trip_id) AS matched_trips,
                    AVG(f.fare_amount) AS avg_fare,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.fare_amount) AS median_fare,
                    AVG(f.trip_distance) AS avg_distance,
                    AVG(f.trip_duration_minutes) AS avg_duration
                FROM gold.fact_trip f
                JOIN gold.dim_driver d ON f.driver_key = d.driver_key
                JOIN gold.dim_date dt ON f.date_key = dt.date_key
                {where_str};
            """

            df_match = execute_read_only_query(query)
            if not df_match.empty and int(df_match.iloc[0]["matched_trips"]) > 0:
                row = df_match.iloc[0]
                matched_count = int(row["matched_trips"])
                avg_fare_val = float(row["avg_fare"])
                est_scenario_rev = avg_fare_val * exp_trips

                coverage_status = "Strong" if matched_count >= 50 else ("Moderate" if matched_count >= 10 else "Limited")
                
                st.markdown(f"### Revenue Scenario Result (Data Coverage: `{coverage_status}` — {matched_count:,} Matched Trips)")
                
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    render_kpi_card("Matched Trips", f"{matched_count:,}", "Database", "Historical Base", "#3B82F6")
                with m2:
                    render_kpi_card("Filtered Avg Fare", f"${avg_fare_val:,.2f}", "TrendingUp", "Ticket Size", "#10B981")
                with m3:
                    render_kpi_card("Expected Volume", f"{exp_trips:,}", "ChartColumn", "Scenario Input", "#F59E0B")
                with m4:
                    render_kpi_card("Estimated Revenue", f"${est_scenario_rev:,.2f}", "TrendingUp", "Calculated Scenario", "#8B5CF6")

                st.info(f"📐 **Transparent Formula:** Filtered Avg Fare (`${avg_fare_val:,.2f}`) × Expected Trips (`{exp_trips:,}`) = **`${est_scenario_rev:,.2f}`**")

                st.session_state.prediction_history.append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "prediction_type": "Revenue Scenario Estimate",
                    "filters": f"{sel_city_rev}, {sel_dist_band}, {exp_trips} trips",
                    "result": f"${est_scenario_rev:,.2f}",
                    "method": "Filtered Historical Yield"
                })
            else:
                st.warning("⚠️ Insufficient historical data matching the selected scenario filters to generate a reliable estimate.")

    # =========================================================================
    # MODE 4: TRIP VOLUME ESTIMATE
    # =========================================================================
    elif pred_type.startswith("4"):
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#3B82F6', 18)} Mode 4: Trip Volume Distribution Estimate</div>""", unsafe_allow_html=True)
        
        v1, v2 = st.columns(2)
        with v1:
            sel_v_city = st.selectbox("Target City", ["All Cities"] + filter_opts["cities"], key="vol_city")
        with v2:
            sel_v_day = st.selectbox("Day Type", ["All Days", "Weekend Only", "Weekday Only"], key="vol_day")

        if st.button("ESTIMATE TRIP VOLUME", key="btn_est_volume", type="primary"):
            df_v = execute_read_only_query("SELECT total_trips FROM gold.revenue_mart;")
            if not df_v.empty:
                avg_v = float(df_v["total_trips"].mean())
                st.markdown(f"### Historical Daily Trip Volume Baseline: `{avg_v:,.0f} trips/day`")
                render_histogram(df_v, "total_trips", bins=15, color="#3B82F6", height=240, title="Daily Trip Volume Distribution")

                st.session_state.prediction_history.append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "prediction_type": "Trip Volume Estimate",
                    "filters": f"{sel_v_city}, {sel_v_day}",
                    "result": f"Baseline {avg_v:,.0f} trips",
                    "method": "Distribution Baseline"
                })

    # =========================================================================
    # MODE 5: SEGMENT PERFORMANCE ANALYSIS
    # =========================================================================
    elif pred_type.startswith("5"):
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Workflow', '#8B5CF6', 18)} Mode 5: Custom Segment Performance Analysis</div>""", unsafe_allow_html=True)

        s1, s2, s3 = st.columns(3)
        with s1:
            seg_city = st.selectbox("City Segment", ["All Cities"] + filter_opts["cities"], key="seg_city")
        with s2:
            seg_pass = st.selectbox("Passenger Segment", ["All Passengers"] + filter_opts["passenger_counts"], key="seg_pass")
        with s3:
            seg_day = st.selectbox("Day Type Segment", ["All Days", "Weekend Only", "Weekday Only"], key="seg_day")

        st.markdown(f"**Active Segment Chips:** `{seg_city}` × `{seg_pass}` × `{seg_day}`")

        if st.button("ANALYZE SEGMENT", key="btn_analyze_segment", type="primary"):
            sql_w = []
            if seg_city != "All Cities":
                sql_w.append(f"d.city = '{seg_city}'")
            if seg_pass != "All Passengers":
                sql_w.append(f"f.passenger_count = {seg_pass}")
            if seg_day == "Weekend Only":
                sql_w.append("dt.is_weekend = TRUE")
            elif seg_day == "Weekday Only":
                sql_w.append("dt.is_weekend = FALSE")

            where_str = ("WHERE " + " AND ".join(sql_w)) if sql_w else ""

            query = f"""
                SELECT 
                    COUNT(f.trip_id) AS matched_trips,
                    COUNT(DISTINCT f.driver_key) AS matched_drivers,
                    SUM(f.fare_amount) AS total_revenue,
                    AVG(f.fare_amount) AS avg_fare,
                    AVG(f.trip_distance) AS avg_distance,
                    AVG(f.trip_duration_minutes) AS avg_duration
                FROM gold.fact_trip f
                JOIN gold.dim_driver d ON f.driver_key = d.driver_key
                JOIN gold.dim_date dt ON f.date_key = dt.date_key
                {where_str};
            """

            df_seg = execute_read_only_query(query)
            if not df_seg.empty and int(df_seg.iloc[0]["matched_trips"]) > 0:
                row = df_seg.iloc[0]
                st.markdown("### Segment Performance Dashboard")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    render_kpi_card("Matching Trips", f"{int(row['matched_trips']):,}", "ChartColumn", "Segment Trips", "#3B82F6")
                with c2:
                    render_kpi_card("Matching Drivers", f"{int(row['matched_drivers']):,}", "Users", "Segment Drivers", "#10B981")
                with c3:
                    render_kpi_card("Segment Revenue", f"${float(row['total_revenue']):,.2f}", "TrendingUp", "Gross Revenue", "#F59E0B")
                with c4:
                    render_kpi_card("Average Fare", f"${float(row['avg_fare']):,.2f}", "Activity", "Yield Per Trip", "#8B5CF6")

                df_trips_scatter = execute_read_only_query("SELECT fare_amount, trip_distance, trip_duration_minutes FROM gold.fact_trip LIMIT 50;")
                render_scatter_chart(df_trips_scatter, "trip_distance", "fare_amount", size_col="trip_duration_minutes", height=280)

                st.session_state.prediction_history.append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "prediction_type": "Segment Analysis",
                    "filters": f"{seg_city}, {seg_pass} pass, {seg_day}",
                    "result": f"{int(row['matched_trips']):,} Trips (${float(row['total_revenue']):,.2f})",
                    "method": "Multi-Dimensional Warehouse Query"
                })

    # =========================================================================
    # MODE 6: ANOMALY SCENARIO ANALYSIS
    # =========================================================================
    elif pred_type.startswith("6"):
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} Mode 6: Statistical Anomaly Scenario Sensitivity Analysis</div>""", unsafe_allow_html=True)
        
        z_sens = st.slider("Z-Score Sensitivity Threshold", 1.0, 3.0, 1.8, step=0.1, key="ps_anom_z")

        if st.button("RUN ANOMALY SCENARIO", key="btn_run_anom_scen", type="primary"):
            anom_res = detect_revenue_anomalies(threshold_z=z_sens)

            if anom_res.get("anomaly_detected"):
                st.warning(f"🚨 Detected {anom_res['anomalies_found_count']} anomaly events across {anom_res['total_days_analyzed']} analyzed days.")
                df_anom = pd.DataFrame(anom_res["anomalies"])
                df_full_rev = execute_read_only_query("SELECT date_key, total_revenue FROM gold.revenue_mart ORDER BY date_key ASC;")

                if not df_full_rev.empty:
                    df_full_rev["date_key"] = df_full_rev["date_key"].astype(str)
                    df_anom_dates = df_anom["date_key"].astype(str).tolist() if "date_key" in df_anom.columns else []
                    df_full_rev["is_anomaly"] = df_full_rev["date_key"].isin(df_anom_dates)
                    render_anomaly_chart(df_full_rev, date_col="date_key", value_col="total_revenue", anomaly_col="is_anomaly", height=300)

                st.dataframe(df_anom, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No statistical revenue anomalies detected at selected Z-threshold.")

    # =========================================================================
    # PREDICTION HISTORY & EXPORT
    # =========================================================================
    st.divider()
    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ClipboardList', '#3B82F6', 20)} Current Session Prediction History</div>""", unsafe_allow_html=True)

    if st.session_state.prediction_history:
        df_hist = pd.DataFrame(st.session_state.prediction_history)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        st.download_button("Export Prediction History CSV", df_hist.to_csv(index=False), "prediction_history.csv", "text/csv")
    else:
        st.info("No predictions executed in current session yet.")
