import streamlit as st
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card


def render_operations_page():
    """Render SaaS Operations Analytics Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Operations Analytics</h1>
            <p>Trip duration, distance distribution, peak hours, and fleet efficiency analytics.</p>
        </div>
    """, unsafe_allow_html=True)

    df_kpi = execute_read_only_query("SELECT * FROM gold.kpi_summary;")
    if not df_kpi.empty:
        k_dict = df_kpi.iloc[0].to_dict()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Avg Trip Distance", f"{float(k_dict.get('average_distance', 0)):,.2f} mi", "Activity", "Fleet Mileage", "#3B82F6", change_text="2.4%", is_positive=True)
        with c2:
            render_kpi_card("Avg Trip Duration", f"{float(k_dict.get('average_trip_duration', 0)):,.1f} min", "Clock", "Transit Time", "#10B981", change_text="1.5%", is_positive=False)
        with c3:
            render_kpi_card("Total Fleet Trips", f"{int(k_dict.get('total_trips', 0)):,}", "ChartColumn", "Total Completed", "#F59E0B", change_text="8.7%", is_positive=True)
        with c4:
            render_kpi_card("Total Revenue", f"${float(k_dict.get('total_revenue', 0)):,.2f}", "TrendingUp", "Gross Revenue", "#8B5CF6", change_text="12.1%", is_positive=True)

    st.divider()

    # Operations Trip Sample Analysis
    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Workflow', '#3B82F6', 18)} Operational Trip Performance Sample</div>""", unsafe_allow_html=True)
    df_trips = execute_read_only_query("SELECT trip_id, fare_amount, trip_distance, trip_duration_minutes, passenger_count FROM gold.fact_trip LIMIT 30;")
    if not df_trips.empty:
        st.scatter_chart(df_trips, x="trip_distance", y="fare_amount", size="trip_duration_minutes", use_container_width=True)
        st.dataframe(df_trips, use_container_width=True, hide_index=True)
