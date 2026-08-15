import pandas as pd
import streamlit as st
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card
from agentic_ai.ui.components.charts import render_multi_metric_chart, render_bar_chart


def render_revenue_page():
    """Render SaaS Revenue Intelligence Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Revenue Intelligence</h1>
            <p>Monitor revenue performance, analyze daily trends and investigate fare optimization.</p>
        </div>
    """, unsafe_allow_html=True)

    # Filter Bar Container
    st.markdown(f"""<div class="filter-bar">{get_icon_svg('SlidersHorizontal', '#3B82F6', 18)} <b>Global Revenue Filters</b></div>""", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        date_filter = st.selectbox("Date Scope", ["All Time (Last 30 Days)", "Recent 15 Days", "Recent 7 Days"])
    with f2:
        day_filter = st.selectbox("Day Type", ["All Days", "Weekend Only", "Weekday Only"])
    with f3:
        sort_by = st.selectbox("Sort Order", ["Date Ascending", "Revenue High to Low"])

    df_rev = execute_read_only_query("SELECT date_key, is_weekend, total_revenue, total_trips, average_fare, average_distance FROM gold.revenue_mart ORDER BY date_key ASC;")

    if not df_rev.empty:
        # Apply filters
        if day_filter == "Weekend Only":
            df_rev = df_rev[df_rev["is_weekend"] == True]
        elif day_filter == "Weekday Only":
            df_rev = df_rev[df_rev["is_weekend"] == False]

        if "15" in date_filter:
            df_rev = df_rev.tail(15)
        elif "7" in date_filter:
            df_rev = df_rev.tail(7)

        if sort_by == "Revenue High to Low":
            df_rev = df_rev.sort_values(by="total_revenue", ascending=False)

        # Top Metric Cards
        tot_rev = df_rev["total_revenue"].sum()
        tot_trips = df_rev["total_trips"].sum()
        avg_fare = df_rev["average_fare"].mean()
        rev_per_trip = tot_rev / tot_trips if tot_trips > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Period Revenue", f"${tot_rev:,.2f}", "TrendingUp", "Selected Scope", "#3B82F6", change_text="14.2%", is_positive=True)
        with c2:
            render_kpi_card("Period Trips", f"{tot_trips:,}", "ChartColumn", "Filtered Volume", "#10B981", change_text="9.5%", is_positive=True)
        with c3:
            render_kpi_card("Average Fare", f"${avg_fare:,.2f}", "TrendingUp", "Mean Ticket Size", "#F59E0B", change_text="3.8%", is_positive=True)
        with c4:
            render_kpi_card("Revenue / Trip", f"${rev_per_trip:,.2f}", "Activity", "Yield Per Trip", "#8B5CF6", change_text="4.1%", is_positive=True)

        st.divider()

        # Tabs: Trends | Weekend Analysis | Detailed Table
        t1, t2, t3 = st.tabs(["Revenue Trends", "Weekend vs Weekday", "Detailed Data Table"])

        with t1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TrendingUp', '#3B82F6', 18)} Revenue & Trip Volume Trend</div>""", unsafe_allow_html=True)
            render_multi_metric_chart(df_rev, "date_key", "total_revenue", "total_trips")

        with t2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('CalendarDays', '#8B5CF6', 18)} Weekend vs Weekday Revenue Metrics</div>""", unsafe_allow_html=True)
            df_full = execute_read_only_query("SELECT is_weekend, SUM(total_revenue) AS total_revenue, AVG(average_fare) AS avg_fare, SUM(total_trips) AS total_trips FROM gold.revenue_mart GROUP BY is_weekend;")
            if not df_full.empty:
                df_full["is_weekend"] = df_full["is_weekend"].map({True: "Weekend", False: "Weekday"})
                render_bar_chart(df_full, "is_weekend", "total_revenue", color="#8B5CF6", title="Total Revenue ($)")
                st.dataframe(df_full, use_container_width=True, hide_index=True)

        with t3:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Database', '#60A5FA', 18)} Revenue Mart Records</div>""", unsafe_allow_html=True)
            st.dataframe(df_rev, use_container_width=True, hide_index=True)
            st.download_button("Download CSV", df_rev.to_csv(index=False), "revenue_mart.csv", "text/csv")
