import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import render_area_chart, render_bar_chart, render_donut_chart


def render_overview_page():
    """Render SaaS Overview Page matching visual dashboard reference standards."""
    st.markdown("""
        <div class="page-header">
            <h1>Overview</h1>
            <p>Enterprise mobility performance and operational intelligence at a glance.</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Fetch Real KPI Metrics from PostgreSQL Gold Warehouse
    try:
        engine = get_engine()
        with engine.connect() as conn:
            kpi_row = conn.execute(text("SELECT * FROM gold.kpi_summary")).mappings().first()

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi_card("Total Revenue", f"${float(kpi_row['total_revenue']):,.2f}", "TrendingUp", "Gold Warehouse", "#3B82F6", change_text="12.4%", is_positive=True)
        with c2:
            render_kpi_card("Total Trips", f"{int(kpi_row['total_trips']):,}", "ChartColumn", "Completed Trips", "#10B981", change_text="8.2%", is_positive=True)
        with c3:
            render_kpi_card("Average Fare", f"${float(kpi_row['average_fare']):,.2f}", "TrendingUp", "Per Trip Avg", "#F59E0B", change_text="3.5%", is_positive=True)
        with c4:
            render_kpi_card("Average Distance", f"{float(kpi_row['average_distance']):,.2f} mi", "Activity", "Trip Miles", "#8B5CF6", change_text="1.8%", is_positive=True)
        with c5:
            render_kpi_card("Average Duration", f"{float(kpi_row['average_trip_duration']):,.1f} min", "Clock", "Trip Duration", "#EC4899", change_text="2.1%", is_positive=False)

        st.divider()

        # 2. Row 1: Charts Grid (Revenue Trend & Trip Volume Trend)
        r1_col1, r1_col2 = st.columns(2)
        df_rev = execute_read_only_query("SELECT date_key, is_weekend, total_revenue, total_trips, average_fare FROM gold.revenue_mart ORDER BY date_key ASC LIMIT 30;")
        
        with r1_col1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#3B82F6', 20)} Revenue Performance Trend</div>""", unsafe_allow_html=True)
            if not df_rev.empty:
                render_area_chart(df_rev, "date_key", "total_revenue", color="#3B82F6", title="Total Revenue ($)")

        with r1_col2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#10B981', 20)} Daily Trip Volume</div>""", unsafe_allow_html=True)
            if not df_rev.empty:
                render_bar_chart(df_rev, "date_key", "total_trips", color="#10B981", title="Total Trips")

        # 3. Row 2: Top Drivers & Weekend Breakdown
        r2_col1, r2_col2 = st.columns([3, 2])
        with r2_col1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Users', '#F59E0B', 20)} Top Drivers Leaderboard</div>""", unsafe_allow_html=True)
            df_top = execute_read_only_query("SELECT driver_name, driver_city, driver_rating, total_revenue, total_trips FROM gold.driver_performance_mart ORDER BY total_revenue DESC LIMIT 5;")
            st.dataframe(df_top, use_container_width=True, hide_index=True)

        with r2_col2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('CalendarDays', '#8B5CF6', 20)} Weekend vs Weekday Revenue Share</div>""", unsafe_allow_html=True)
            if not df_rev.empty and "is_weekend" in df_rev.columns:
                weekend_summary = df_rev.groupby("is_weekend")[["total_revenue", "total_trips"]].sum().reset_index()
                weekend_summary["is_weekend"] = weekend_summary["is_weekend"].map({True: "Weekend", False: "Weekday"})
                render_donut_chart(weekend_summary, "is_weekend", "total_revenue", height=240)

        # 4. Row 3: Recent Activity Panel
        st.divider()
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Activity', '#EC4899', 20)} Recent System & Agent Activity</div>""", unsafe_allow_html=True)
        
        with engine.connect() as conn:
            df_act = pd.read_sql_query(text("SELECT batch_id, task_name, target_table, rows_inserted, status, end_time FROM audit.etl_batch_log ORDER BY batch_id DESC LIMIT 5;"), conn)
            
        if not df_act.empty:
            df_act["status"] = df_act["status"].apply(render_status_pill)
            st.dataframe(df_act[["batch_id", "task_name", "target_table", "rows_inserted", "status", "end_time"]], use_container_width=True, hide_index=True)

    except Exception as ex:
        st.error(f"Could not load Overview data: {ex}")
