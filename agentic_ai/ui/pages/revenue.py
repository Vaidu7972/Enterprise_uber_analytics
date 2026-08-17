import pandas as pd
import streamlit as st
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card
from agentic_ai.ui.components.charts import render_multi_metric_chart, render_bar_chart, render_area_chart

def render_revenue_page():
    """Render SaaS Revenue Intelligence Page with real calculated metrics and interactive filters."""
    st.markdown("""
        <div class="page-header">
            <h1>Revenue Intelligence</h1>
            <p>Monitor revenue performance, analyze daily trends, and investigate fare yield optimization.</p>
        </div>
    """, unsafe_allow_html=True)

    # Filter Bar Container
    st.markdown(f"""<div class="filter-bar">{get_icon_svg('SlidersHorizontal', '#3B82F6', 18)} <b>Global Revenue Scope & Filter Controls</b></div>""", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        date_filter = st.selectbox("Date Scope", ["All Time (Last 30 Days)", "Recent 15 Days", "Recent 7 Days"], key="rev_date_scope")
    with f2:
        day_filter = st.selectbox("Day Type", ["All Days", "Weekend Only", "Weekday Only"], key="rev_day_type")
    with f3:
        sort_by = st.selectbox("Sort Order", ["Date Ascending", "Revenue High to Low"], key="rev_sort_order")

    df_full = execute_read_only_query("SELECT date_key, is_weekend, total_revenue, total_trips, average_fare, average_distance FROM gold.revenue_mart ORDER BY date_key ASC;")

    if not df_full.empty:
        df_rev = df_full.copy()

        # Apply Day Type Filter
        if day_filter == "Weekend Only":
            df_rev = df_rev[df_rev["is_weekend"] == True]
        elif day_filter == "Weekday Only":
            df_rev = df_rev[df_rev["is_weekend"] == False]

        # Apply Date Scope Filter
        if "15" in date_filter:
            df_rev = df_rev.tail(15)
        elif "7" in date_filter:
            df_rev = df_rev.tail(7)

        # Apply Sorting
        if sort_by == "Revenue High to Low":
            df_rev = df_rev.sort_values(by="total_revenue", ascending=False)

        # Calculate Period Metrics
        tot_rev = df_rev["total_revenue"].sum()
        tot_trips = df_rev["total_trips"].sum()
        avg_fare = df_rev["average_fare"].mean()
        rev_per_trip = tot_rev / tot_trips if tot_trips > 0 else 0

        # Calculate Real Deltas comparing filtered subset vs preceding equal window if enough rows
        rev_delta_str = "Filtered Scope"
        trips_delta_str = "Filtered Scope"
        is_rev_pos = True
        is_trips_pos = True

        if len(df_full) >= len(df_rev) * 2 and len(df_rev) > 0:
            sub_len = len(df_rev)
            curr_window = df_full.tail(sub_len)
            prev_window = df_full.iloc[-(sub_len*2):-sub_len]

            c_r, p_r = curr_window["total_revenue"].sum(), prev_window["total_revenue"].sum()
            if p_r > 0:
                d_r = ((c_r - p_r) / p_r) * 100
                rev_delta_str = f"{d_r:+.1f}%"
                is_rev_pos = d_r >= 0

            c_t, p_t = curr_window["total_trips"].sum(), prev_window["total_trips"].sum()
            if p_t > 0:
                d_t = ((c_t - p_t) / p_t) * 100
                trips_delta_str = f"{d_t:+.1f}%"
                is_trips_pos = d_t >= 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Period Revenue", f"${tot_rev:,.2f}", "TrendingUp", "Selected Scope", "#3B82F6", change_text=rev_delta_str, is_positive=is_rev_pos)
        with c2:
            render_kpi_card("Period Trips", f"{tot_trips:,}", "ChartColumn", "Filtered Volume", "#10B981", change_text=trips_delta_str, is_positive=is_trips_pos)
        with c3:
            render_kpi_card("Average Fare", f"${avg_fare:,.2f}", "TrendingUp", "Mean Ticket Size", "#F59E0B", change_text="Mean Yield", is_positive=True)
        with c4:
            render_kpi_card("Revenue / Trip", f"${rev_per_trip:,.2f}", "Activity", "Yield Per Trip", "#8B5CF6", change_text="Calculated Yield", is_positive=True)

        st.divider()

        # Tabs: Trends | Average Fare | Weekend Breakdown | Detailed Table
        t1, t2, t3, t4 = st.tabs(["Revenue & Volume Trends", "Average Fare Trend", "Weekend vs Weekday", "Detailed Data Table"])

        with t1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#3B82F6', 18)} Revenue & Trip Volume Time Series</div>""", unsafe_allow_html=True)
            render_multi_metric_chart(df_rev, "date_key", "total_revenue", "total_trips")

        with t2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#F59E0B', 18)} Average Fare Yield Trend</div>""", unsafe_allow_html=True)
            render_area_chart(df_rev, "date_key", "average_fare", color="#F59E0B", title="Average Fare ($)")

        with t3:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('CalendarDays', '#8B5CF6', 18)} Weekend vs Weekday Revenue Metrics</div>""", unsafe_allow_html=True)
            df_wk = execute_read_only_query("SELECT is_weekend, SUM(total_revenue) AS total_revenue, AVG(average_fare) AS avg_fare, SUM(total_trips) AS total_trips FROM gold.revenue_mart GROUP BY is_weekend;")
            if not df_wk.empty:
                df_wk["is_weekend"] = df_wk["is_weekend"].map({True: "Weekend", False: "Weekday"})
                render_bar_chart(df_wk, "is_weekend", "total_revenue", color="#8B5CF6", title="Total Revenue ($)")
                st.dataframe(df_wk, use_container_width=True, hide_index=True)

        with t4:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Database', '#06B6D4', 18)} Revenue Mart Records</div>""", unsafe_allow_html=True)
            st.dataframe(df_rev, use_container_width=True, hide_index=True)
            st.download_button("Download CSV Data", df_rev.to_csv(index=False), "revenue_mart.csv", "text/csv")
