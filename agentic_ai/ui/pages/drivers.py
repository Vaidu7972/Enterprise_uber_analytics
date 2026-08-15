import pandas as pd
import streamlit as st
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card


def render_drivers_page():
    """Render SaaS Driver Intelligence Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Driver Intelligence</h1>
            <p>Individual driver performance history, rating analytics, and ML underperformance risk predictions.</p>
        </div>
    """, unsafe_allow_html=True)

    df_drivers = execute_read_only_query("SELECT driver_id, driver_name, driver_city, driver_rating, total_revenue, total_trips, average_fare, average_distance FROM gold.driver_performance_mart ORDER BY total_revenue DESC;")

    if not df_drivers.empty:
        # Driver Selector Top Container
        st.markdown(f"""<div class="filter-bar">{get_icon_svg('Users', '#F59E0B', 18)} <b>Select Driver Profile</b></div>""", unsafe_allow_html=True)
        driver_list = df_drivers["driver_id"].tolist()
        selected_driver = st.selectbox("Driver ID", driver_list)

        drv_info = df_drivers[df_drivers["driver_id"] == selected_driver].iloc[0]

        # Top KPI Cards for Selected Driver
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Driver Name", drv_info["driver_name"], "Users", f"City: {drv_info['driver_city']}", "#3B82F6", change_text="Verified Driver", is_positive=True)
        with c2:
            render_kpi_card("Driver Rating", f"{drv_info['driver_rating']:.2f}", "ShieldCheck", "Performance Rating", "#10B981", change_text="Top Tier", is_positive=True)
        with c3:
            render_kpi_card("Total Revenue", f"${float(drv_info['total_revenue']):,.2f}", "TrendingUp", "Lifetime Earnings", "#F59E0B", change_text="Revenue Share", is_positive=True)
        with c4:
            render_kpi_card("Total Trips", f"{int(drv_info['total_trips']):,}", "ChartColumn", "Trips Completed", "#8B5CF6", change_text="Completed", is_positive=True)

        st.divider()

        # Tabs: Performance | ML Risk Assessment | All Driver Rankings
        t1, t2, t3 = st.tabs(["Performance History", "ML Risk Assessment", "All Driver Rankings"])

        with t1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#3B82F6', 18)} Individual Driver Metrics</div>""", unsafe_allow_html=True)
            d_df = pd.DataFrame([drv_info.to_dict()])
            st.dataframe(d_df, use_container_width=True, hide_index=True)

        with t2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('BrainCircuit', '#F59E0B', 18)} ML Driver Underperformance Risk Score</div>""", unsafe_allow_html=True)
            ml_res = predict_driver_risk(driver_id=selected_driver)
            if ml_res.get("found"):
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Risk Level", ml_res.get("risk_level", "Unknown"))
                with m2:
                    st.metric("Risk Probability", f"{round(ml_res.get('risk_probability', 0)*100, 2)}%")
                with m3:
                    st.metric("Scored Trips", ml_res.get("total_trips", 0))
                st.info(f"Driver `{selected_driver}` is scored using trained RandomForest features from the Gold warehouse.")

        with t3:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Users', '#EC4899', 18)} Full Driver Leaderboard</div>""", unsafe_allow_html=True)
            st.dataframe(df_drivers, use_container_width=True, hide_index=True)
