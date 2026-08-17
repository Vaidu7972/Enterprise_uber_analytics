import pandas as pd
import streamlit as st
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import (
    render_donut_chart,
    render_horizontal_bar_chart,
    render_bar_chart,
    render_anomaly_chart,
)

def render_predictions_page():
    """Render SaaS Predictive Intelligence Page covering ML risk, demand estimation, and anomaly detection."""
    st.markdown("""
        <div class="page-header">
            <h1>Predictive Intelligence</h1>
            <p>RandomForest driver risk scoring, historical mobility demand estimation, and z-score anomaly detection.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_risk, tab_forecast, tab_anomaly = st.tabs([
        "🤖 Driver Risk Scoring (ML)", 
        "📈 Historical Demand Estimate", 
        "🚨 Anomaly Detection Engine"
    ])

    # TAB A: Driver Risk Scoring
    with tab_risk:
        batch_ml = predict_driver_risk()
        if batch_ml.get("found"):
            total_scored = batch_ml.get('total_drivers_scored', 0)
            high_cnt = batch_ml.get('high_risk_count', 0)
            med_cnt = batch_ml.get('medium_risk_count', 0)
            low_cnt = batch_ml.get('low_risk_count', 0)

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                render_kpi_card("Scored Drivers", f"{total_scored}", "Users", "Total Fleet Drivers", "#3B82F6", change_text="Active ML Model", is_positive=True)
            with m2:
                render_kpi_card("High Risk", f"{high_cnt}", "TriangleAlert", "Requires Action", "#EF4444", change_text="High Risk", is_positive=False)
            with m3:
                render_kpi_card("Medium Risk", f"{med_cnt}", "Clock", "Monitor Performance", "#F59E0B", change_text="Watch List", is_positive=True)
            with m4:
                render_kpi_card("Low Risk", f"{low_cnt}", "CircleCheck", "Optimal Performance", "#10B981", change_text="Optimal", is_positive=True)

            st.divider()

            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.markdown(f"""<div class="saas-card-title">{get_icon_svg('PieChart', '#3B82F6', 18)} Risk Level Distribution</div>""", unsafe_allow_html=True)
                risk_df = pd.DataFrame([
                    {"Risk Level": "High Risk", "Drivers": high_cnt},
                    {"Risk Level": "Medium Risk", "Drivers": med_cnt},
                    {"Risk Level": "Low Risk", "Drivers": low_cnt},
                ])
                render_donut_chart(risk_df, "Risk Level", "Drivers", height=240)

            with r_col2:
                meta = batch_ml.get("model_info", {})
                if meta.get("importances"):
                    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('BrainCircuit', '#8B5CF6', 18)} RandomForest Feature Importances</div>""", unsafe_allow_html=True)
                    imp_df = pd.DataFrame(list(meta["importances"].items()), columns=["Feature", "Importance"]).sort_values(by="Importance", ascending=False)
                    render_horizontal_bar_chart(imp_df, "Feature", "Importance", color="#8B5CF6", height=240)

            st.divider()

            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} High-Risk Driver Table</div>""", unsafe_allow_html=True)
            top_high = pd.DataFrame(batch_ml.get("top_high_risk_drivers", []))
            if not top_high.empty:
                st.dataframe(top_high, use_container_width=True, hide_index=True)
            else:
                st.info("No high-risk drivers currently identified by ML model.")

    # TAB B: Demand Estimation & Forecasting
    with tab_forecast:
        from agentic_ai.ml.demand_forecasting import predict_demand
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#3B82F6', 18)} Historical Demand Estimate & Volume Forecast</div>""", unsafe_allow_html=True)
        st.caption("ℹ️ **Model Basis:** Historical Gold Warehouse Aggregation & Peak-Hour Operational Multipliers.")

        fc_c1, fc_c2 = st.columns(2)
        with fc_c1:
            fc_city = st.selectbox("Target City Scope", ["All Cities / System Wide", "Pune", "Mumbai", "Delhi", "Bangalore", "Hyderabad"], key="fc_city_sel")
        with fc_c2:
            fc_hour = st.slider("Forecast Target Hour (0-23)", 0, 23, 18, key="fc_hour_sld")

        city_param = None if fc_city.startswith("All") else fc_city
        fc_res = predict_demand(city=city_param, hour=fc_hour)

        if fc_res.get("success"):
            f1, f2, f3 = st.columns(3)
            with f1:
                render_kpi_card("Estimated Trips", f"{fc_res['predicted_trips']}", "ChartColumn", f"Target Hour {fc_res['target_hour']}:00", "#3B82F6")
            with f2:
                render_kpi_card("Expected Revenue", f"${fc_res['predicted_revenue']:,.2f}", "TrendingUp", f"Avg Fare ${fc_res['expected_avg_fare']:.2f}", "#10B981")
            with f3:
                render_kpi_card("Demand Level", f"{fc_res['demand_level']}", "Activity", "Hourly Window", "#F59E0B")

            st.markdown(f"**Operational Recommendation:** {fc_res['recommendation']}")

            if fc_res.get("high_demand_zones"):
                st.markdown(f"**High Demand Zones:** `{', '.join(fc_res['high_demand_zones'])}`")
                zones_df = pd.DataFrame([{"Zone": z, "Weight": (idx+1)*10} for idx, z in enumerate(fc_res["high_demand_zones"])])
                render_bar_chart(zones_df, "Zone", "Weight", color="#F59E0B", title="Demand Density Weight", height=200)

    # TAB C: Anomaly Detection Engine
    with tab_anomaly:
        from agentic_ai.ml.anomaly_detection import detect_revenue_anomalies
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} Statistical Anomaly Detection (Z-Score Thresholding)</div>""", unsafe_allow_html=True)

        thresh = st.slider("Z-Score Sensitivity Threshold", 1.0, 3.0, 1.8, step=0.1, key="anom_thresh_slider")
        anom_res = detect_revenue_anomalies(threshold_z=thresh)

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
            st.success("✅ No statistical revenue or trip volume anomalies detected within selected Z-threshold.")
