import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import (
    render_calendar_heatmap,
    render_bubble_scatter,
    render_horizontal_bar_chart,
    render_donut_chart,
)


def render_overview_page():
    """Render Executive Command Center Overview Page with real calculated warehouse analytics."""
    st.markdown("""
        <div class="page-header">
            <h1>Executive Command Center</h1>
            <p>Real-time enterprise mobility intelligence, daily revenue heatmap, volume scatter analysis, and system telemetry.</p>
        </div>
    """, unsafe_allow_html=True)

    # Quick Action Banner for Prediction Studio Navigation
    q_col1, q_col2 = st.columns([3, 1])
    with q_col1:
        st.markdown(f"""
            <div style="background:rgba(139,92,246,0.12); border:1px solid rgba(139,92,246,0.3); border-radius:12px; padding:12px 16px; display:flex; align-items:center; gap:12px;">
                {get_icon_svg('Sparkles', '#8B5CF6', 22)}
                <div>
                    <div style="font-weight:800; font-size:0.95rem; color:#F8FAFC;">Custom Mobility Scenario & What-If Predictions</div>
                    <div style="font-size:0.8rem; color:#94A3B8;">Build custom demand, driver risk what-if, or revenue scenario estimates in Prediction Studio.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with q_col2:
        if st.button("⚡ Open Prediction Studio", key="btn_ov_to_studio", use_container_width=True, type="primary"):
            st.session_state.current_page = "Prediction Studio"
            st.rerun()

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            kpi_row = conn.execute(text("SELECT * FROM gold.kpi_summary")).mappings().first()

        df_rev = execute_read_only_query(
            "SELECT date_key, is_weekend, total_revenue, total_trips, average_fare, average_distance FROM gold.revenue_mart ORDER BY date_key ASC;"
        )

        if df_rev.empty:
            st.info("No revenue records are available for this period.")
            return

        df_rev["total_revenue"] = df_rev["total_revenue"].astype(float)
        df_rev["total_trips"] = df_rev["total_trips"].astype(int)
        df_rev["average_fare"] = df_rev["average_fare"].astype(float)
        df_rev["average_distance"] = df_rev["average_distance"].astype(float)

        rev_change = "No prior-period comparison"
        trips_change = "No prior-period comparison"
        fare_change = "No prior-period comparison"
        dist_change = "No prior-period comparison"

        is_rev_pos, is_trips_pos, is_fare_pos, is_dist_pos = True, True, True, True

        if len(df_rev) >= 14:
            curr_7 = df_rev.tail(7)
            prev_7 = df_rev.iloc[-14:-7]

            c_rev, p_rev = curr_7["total_revenue"].sum(), prev_7["total_revenue"].sum()
            if p_rev > 0:
                d_rev = ((c_rev - p_rev) / p_rev) * 100
                rev_change = f"{d_rev:+.1f}%"
                is_rev_pos = d_rev >= 0

            c_trips, p_trips = curr_7["total_trips"].sum(), prev_7["total_trips"].sum()
            if p_trips > 0:
                d_trips = ((c_trips - p_trips) / p_trips) * 100
                trips_change = f"{d_trips:+.1f}%"
                is_trips_pos = d_trips >= 0

            c_fare, p_fare = curr_7["average_fare"].mean(), prev_7["average_fare"].mean()
            if p_fare > 0:
                d_fare = ((c_fare - p_fare) / p_fare) * 100
                fare_change = f"{d_fare:+.1f}%"
                is_fare_pos = d_fare >= 0

            c_dist, p_dist = curr_7["average_distance"].mean(), prev_7["average_distance"].mean()
            if p_dist > 0:
                d_dist = ((c_dist - p_dist) / p_dist) * 100
                dist_change = f"{d_dist:+.1f}%"
                is_dist_pos = d_dist >= 0

        # KPI Summary Cards
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi_card("Total Revenue", f"${float(kpi_row['total_revenue']):,.2f}", "TrendingUp", "Gold Warehouse", "#3B82F6", change_text=rev_change, is_positive=is_rev_pos)
        with c2:
            render_kpi_card("Total Trips", f"{int(kpi_row['total_trips']):,}", "ChartColumn", "Completed Trips", "#10B981", change_text=trips_change, is_positive=is_trips_pos)
        with c3:
            render_kpi_card("Average Fare", f"${float(kpi_row['average_fare']):,.2f}", "TrendingUp", "Per Trip Yield", "#F59E0B", change_text=fare_change, is_positive=is_fare_pos)
        with c4:
            render_kpi_card("Average Distance", f"{float(kpi_row['average_distance']):,.2f} mi", "Activity", "Fleet Mileage", "#8B5CF6", change_text=dist_change, is_positive=is_dist_pos)
        with c5:
            render_kpi_card("Average Duration", f"{float(kpi_row['average_trip_duration']):,.1f} min", "Clock", "Trip Transit Time", "#EC4899", change_text="No prior-period comparison", is_positive=True)

        st.divider()

        # =========================================================================
        # TOP ROW: HEATMAP (LEFT) vs BUBBLE SCATTER (RIGHT)
        # =========================================================================
        r1_col1, r1_col2 = st.columns(2)

        # -------------------------------------------------------------------------
        # LEFT: GRAPH 1 — DAILY REVENUE INTENSITY HEATMAP
        # -------------------------------------------------------------------------
        with r1_col1:
            st.markdown(f"""
                <div style="background:#151D2F; border:1px solid rgba(148,163,184,0.16); border-radius:14px; padding:18px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                        <div>
                            <div style="font-weight:800; font-size:1.05rem; color:#F8FAFC; display:flex; align-items:center; gap:8px;">
                                {get_icon_svg('CalendarDays', '#06B6D4', 20)} Daily Revenue Intensity
                            </div>
                            <div style="font-size:0.78rem; color:#94A3B8; margin-top:2px;">Identify high and low revenue days across the selected period.</div>
                        </div>
                        <div style="font-size:0.7rem; font-weight:700; color:#94A3B8; background:rgba(148,163,184,0.12); padding:3px 8px; border-radius:6px;">
                            LOW ➔ HIGH
                        </div>
                    </div>
            """, unsafe_allow_html=True)

            render_calendar_heatmap(df_rev, date_col="date_key", value_col="total_revenue", height=230)

            # Dynamic Insight Calculation for Heatmap
            max_rev_idx = df_rev["total_revenue"].idxmax()
            min_rev_idx = df_rev["total_revenue"].idxmin()
            
            max_rev_row = df_rev.loc[max_rev_idx]
            min_rev_row = df_rev.loc[min_rev_idx]

            max_rev_dt = pd.to_datetime(max_rev_row["date_key"]).strftime("%b %d")
            min_rev_dt = pd.to_datetime(min_rev_row["date_key"]).strftime("%b %d")

            max_rev_val = float(max_rev_row["total_revenue"])
            min_rev_val = float(min_rev_row["total_revenue"])
            avg_rev_val = float(df_rev["total_revenue"].mean())

            st.markdown(f"""
                <div style="margin-top:12px; padding:10px 12px; background:rgba(6,182,212,0.08); border-left:3px solid #06B6D4; border-radius:6px; font-size:0.8rem; color:#CBD5E1;">
                    💡 <b>Dynamic Insight:</b> <b>{max_rev_dt}</b> generated the highest daily revenue (<b>${max_rev_val:,.2f}</b>) in the selected period, while <b>{min_rev_dt}</b> recorded the lowest (<b>${min_rev_val:,.2f}</b>). Average daily revenue was <b>${avg_rev_val:,.2f}</b>.
                </div>
                </div>
            """, unsafe_allow_html=True)

        # -------------------------------------------------------------------------
        # RIGHT: GRAPH 2 — REVENUE vs TRIP VOLUME BUBBLE SCATTER
        # -------------------------------------------------------------------------
        with r1_col2:
            st.markdown(f"""
                <div style="background:#151D2F; border:1px solid rgba(59,130,246,0.3); border-radius:14px; padding:18px;">
                    <div style="margin-bottom:8px;">
                        <div style="font-weight:800; font-size:1.05rem; color:#F8FAFC; display:flex; align-items:center; gap:8px;">
                            {get_icon_svg('ScatterChart', '#3B82F6', 20)} Revenue vs Trip Volume
                        </div>
                        <div style="font-size:0.78rem; color:#94A3B8; margin-top:2px;">Relationship between daily trip volume and generated revenue.</div>
                    </div>
            """, unsafe_allow_html=True)

            render_bubble_scatter(
                df_rev,
                x_col="total_trips",
                y_col="total_revenue",
                size_col="average_fare",
                category_col="is_weekend",
                height=230,
            )

            # Pearson Correlation & Analytics Calculations
            corr_val = float(df_rev["total_trips"].corr(df_rev["total_revenue"]))
            
            if corr_val >= 0.70:
                corr_interp = "Strong Positive Relationship"
            elif corr_val >= 0.40:
                corr_interp = "Moderate Positive Relationship"
            elif corr_val >= 0.10:
                corr_interp = "Weak Positive Relationship"
            elif corr_val >= -0.09:
                corr_interp = "Very Weak Relationship"
            elif corr_val >= -0.39:
                corr_interp = "Weak Negative Relationship"
            elif corr_val >= -0.69:
                corr_interp = "Moderate Negative Relationship"
            else:
                corr_interp = "Strong Negative Relationship"

            max_trips_idx = df_rev["total_trips"].idxmax()
            max_trips_row = df_rev.loc[max_trips_idx]
            max_trips_dt = pd.to_datetime(max_trips_row["date_key"]).strftime("%b %d")
            max_trips_val = int(max_trips_row["total_trips"])

            # 3 Analytical Cards Below Scatter
            sc_c1, sc_c2, sc_c3 = st.columns(3)
            with sc_c1:
                st.markdown(f"""
                    <div style="background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.25); border-radius:10px; padding:8px 10px; text-align:center;">
                        <div style="font-size:0.68rem; font-weight:700; color:#06B6D4; text-transform:uppercase;">Highest Revenue</div>
                        <div style="font-size:1.05rem; font-weight:800; color:#F8FAFC; margin-top:2px;">${max_rev_val/1000:,.1f}K</div>
                        <div style="font-size:0.72rem; color:#94A3B8;">{max_rev_dt}</div>
                    </div>
                """, unsafe_allow_html=True)
            with sc_c2:
                st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.25); border-radius:10px; padding:8px 10px; text-align:center;">
                        <div style="font-size:0.68rem; font-weight:700; color:#10B981; text-transform:uppercase;">Highest Volume</div>
                        <div style="font-size:1.05rem; font-weight:800; color:#F8FAFC; margin-top:2px;">{max_trips_val} trips</div>
                        <div style="font-size:0.72rem; color:#94A3B8;">{max_trips_dt}</div>
                    </div>
                """, unsafe_allow_html=True)
            with sc_c3:
                st.markdown(f"""
                    <div style="background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.25); border-radius:10px; padding:8px 10px; text-align:center;">
                        <div style="font-size:0.68rem; font-weight:700; color:#8B5CF6; text-transform:uppercase;">Trips ↔ Revenue</div>
                        <div style="font-size:1.05rem; font-weight:800; color:#F8FAFC; margin-top:2px;">{corr_val:.2f}</div>
                        <div style="font-size:0.68rem; color:#94A3B8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{corr_interp}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # =========================================================================
        # ROW 2: TOP DRIVERS LEADERBOARD & WEEKEND BREAKDOWN
        # =========================================================================
        r2_col1, r2_col2 = st.columns([3, 2])
        with r2_col1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Users', '#F59E0B', 20)} Top Drivers Leaderboard</div>""", unsafe_allow_html=True)
            df_top = execute_read_only_query("SELECT driver_name, driver_city, driver_rating, total_revenue, total_trips FROM gold.driver_performance_mart ORDER BY total_revenue DESC LIMIT 5;")
            if not df_top.empty:
                render_horizontal_bar_chart(df_top, "driver_name", "total_revenue", color="#F59E0B", title="Driver Revenue ($)", height=220)
                st.dataframe(df_top, use_container_width=True, hide_index=True)

        with r2_col2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('CalendarDays', '#8B5CF6', 20)} Weekend vs Weekday Revenue Share</div>""", unsafe_allow_html=True)
            if not df_rev.empty and "is_weekend" in df_rev.columns:
                weekend_summary = df_rev.groupby("is_weekend")[["total_revenue", "total_trips"]].sum().reset_index()
                weekend_summary["is_weekend"] = weekend_summary["is_weekend"].map({True: "Weekend", False: "Weekday"})
                render_donut_chart(weekend_summary, "is_weekend", "total_revenue", height=240)

        # =========================================================================
        # ROW 3: RECENT ACTIVITY PANEL
        # =========================================================================
        st.divider()
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Activity', '#EC4899', 20)} Recent Airflow Pipeline Batch Ingestion</div>""", unsafe_allow_html=True)
        
        with engine.connect() as conn:
            df_act = pd.read_sql_query(text("SELECT batch_id, task_name, target_table, rows_inserted, status, end_time FROM audit.etl_batch_log ORDER BY batch_id DESC LIMIT 5;"), conn)
            
        if not df_act.empty:
            df_act["status"] = df_act["status"].apply(render_status_pill)
            st.dataframe(df_act[["batch_id", "task_name", "target_table", "rows_inserted", "status", "end_time"]], use_container_width=True, hide_index=True)

    except Exception as ex:
        st.error(f"Could not load Executive Command Center data: {ex}")
