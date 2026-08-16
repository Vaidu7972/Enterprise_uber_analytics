import pandas as pd
import streamlit as st
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card


def render_predictions_page():
    """Render SaaS Predictive Intelligence Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Predictive Intelligence</h1>
            <p>RandomForest machine learning risk scoring on Gold warehouse driver features.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_risk, tab_forecast, tab_anomaly = st.tabs([
        "🤖 Driver Underperformance Risk", 
        "📈 Mobility Demand Forecasting", 
        "🚨 Anomaly Detection Engine"
    ])

    with tab_risk:
        batch_ml = predict_driver_risk()
        if batch_ml.get("found"):
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                render_kpi_card("Scored Drivers", f"{batch_ml.get('total_drivers_scored')}", "Users", "Total Fleet Drivers", "#3B82F6", change_text="Active ML Model", is_positive=True)
            with m2:
                render_kpi_card("High Risk", f"{batch_ml.get('high_risk_count')}", "TriangleAlert", "Requires Action", "#EF4444", change_text="High Risk", is_positive=False)
            with m3:
                render_kpi_card("Medium Risk", f"{batch_ml.get('medium_risk_count')}", "Clock", "Monitor Performance", "#F59E0B", change_text="Watch", is_positive=True)
            with m4:
                render_kpi_card("Low Risk", f"{batch_ml.get('low_risk_count')}", "CircleCheck", "Optimal Performance", "#10B981", change_text="Optimal", is_positive=True)

            st.divider()

            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} High-Risk Driver Leaderboard</div>""", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(batch_ml.get("top_high_risk_drivers", [])), use_container_width=True, hide_index=True)

            meta = batch_ml.get("model_info", {})
            if meta.get("importances"):
                st.divider()
                st.markdown(f"""<div class="saas-card-title">{get_icon_svg('BrainCircuit', '#8B5CF6', 18)} Feature Importances</div>""", unsafe_allow_html=True)
                st.bar_chart(pd.Series(meta["importances"]))

    with tab_forecast:
        from agentic_ai.ml.demand_forecasting import predict_demand
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#3B82F6', 18)} Mobility Demand & Trip Forecast</div>""", unsafe_allow_html=True)
        fc_city = st.selectbox("Select Target City", ["All Cities / System Wide", "Pune", "Mumbai", "Delhi", "Bangalore", "Hyderabad"], key="fc_city_sel")
        fc_hour = st.slider("Select Forecast Target Hour", 0, 23, 18, key="fc_hour_sld")
        
        city_param = None if fc_city.startswith("All") else fc_city
        fc_res = predict_demand(city=city_param, hour=fc_hour)
        
        if fc_res.get("success"):
            f1, f2, f3 = st.columns(3)
            with f1:
                render_kpi_card("Predicted Trips", f"{fc_res['predicted_trips']}", "ChartColumn", f"Target {fc_res['target_hour']}", "#3B82F6")
            with f2:
                render_kpi_card("Expected Revenue", f"${fc_res['predicted_revenue']:,.2f}", "TrendingUp", f"Avg Fare ${fc_res['expected_avg_fare']}", "#10B981")
            with f3:
                render_kpi_card("Demand Level", f"{fc_res['demand_level']}", "Activity", "Peak Window", "#F59E0B")
            
            st.markdown(f"**Operational Recommendation:** {fc_res['recommendation']}")
            st.markdown(f"**High Demand Zones:** {', '.join(fc_res['high_demand_zones'])}")

    with tab_anomaly:
        from agentic_ai.ml.anomaly_detection import detect_revenue_anomalies
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} Statistical Anomaly Detection (Revenue & Trip Variance)</div>""", unsafe_allow_html=True)
        anom_res = detect_revenue_anomalies(threshold_z=1.8)
        
        if anom_res.get("anomaly_detected"):
            st.warning(f"🚨 Detected {anom_res['anomalies_found_count']} anomaly events across {anom_res['total_days_analyzed']} analyzed days.")
            df_anom = pd.DataFrame(anom_res["anomalies"])
            st.dataframe(df_anom, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No statistical revenue or trip volume anomalies detected within Z-threshold.")
