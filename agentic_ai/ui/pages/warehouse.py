import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.tools.sql_tool import get_gold_schema, execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card

GOLD_TABLES = [
    "fact_trip",
    "dim_driver",
    "dim_customer",
    "dim_date",
    "dim_weather",
    "kpi_summary",
    "revenue_mart",
    "driver_performance_mart",
    "action_logs",
    "agent_audit_logs",
]

def render_warehouse_page():
    """Render SaaS Warehouse Explorer Page with Star-Schema visual representation."""
    st.markdown("""
        <div class="page-header">
            <h1>Warehouse Explorer</h1>
            <p>Read-only Gold star-schema visualization, table structures, and safe SQL query runner.</p>
        </div>
    """, unsafe_allow_html=True)

    # Star-Schema Visual Diagram Card
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    bg_card = "#111827" if is_dark else "#FFFFFF"
    border_card = "rgba(148,163,184,0.14)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"

    st.markdown(f"""
        <div style="background:{bg_card}; border:1px solid {border_card}; border-radius:14px; padding:20px; margin-bottom:1.5rem; box-shadow:0 4px 16px rgba(0,0,0,0.15);">
            <div style="display:flex; align-items:center; gap:8px; font-weight:700; font-size:1.05rem; color:{text_primary}; margin-bottom:14px;">
                {get_icon_svg('Database', '#3B82F6', 20)} Gold Data Warehouse Star-Schema Architecture
            </div>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin-bottom:14px;">
                <div style="background:rgba(59,130,246,0.12); border:1px solid rgba(59,130,246,0.3); border-radius:10px; padding:12px; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:#3B82F6;">SCD TYPE 2 DIMENSION</div>
                    <div style="font-weight:800; color:{text_primary}; margin-top:4px;">gold.dim_driver</div>
                </div>
                <div style="background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:12px; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:#10B981;">SCD TYPE 2 DIMENSION</div>
                    <div style="font-weight:800; color:{text_primary}; margin-top:4px;">gold.dim_customer</div>
                </div>
                <div style="background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.3); border-radius:10px; padding:12px; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:#F59E0B;">TEMPORAL DIMENSION</div>
                    <div style="font-weight:800; color:{text_primary}; margin-top:4px;">gold.dim_date</div>
                </div>
                <div style="background:rgba(139,92,246,0.12); border:1px solid rgba(139,92,246,0.3); border-radius:10px; padding:12px; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:#8B5CF6;">ENVIRONMENT DIMENSION</div>
                    <div style="font-weight:800; color:{text_primary}; margin-top:4px;">gold.dim_weather</div>
                </div>
            </div>
            <div style="background:linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(37,99,235,0.2) 100%); border:2px solid #3B82F6; border-radius:12px; padding:14px; text-align:center; margin-bottom:14px;">
                <div style="font-size:0.8rem; font-weight:800; color:#60A5FA; letter-spacing:1px;">CENTRAL FACT TABLE</div>
                <div style="font-size:1.2rem; font-weight:800; color:#FFFFFF; margin-top:2px;">gold.fact_trip</div>
                <div style="font-size:0.78rem; color:#94A3B8; margin-top:2px;">Measures: fare_amount, trip_distance, trip_duration_minutes, passenger_count</div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:12px;">
                <div style="background:rgba(6,182,212,0.12); border:1px solid rgba(6,182,212,0.3); border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:700; color:#06B6D4;">AGGREGATED MART</div>
                    <div style="font-weight:700; color:{text_primary};">gold.kpi_summary</div>
                </div>
                <div style="background:rgba(6,182,212,0.12); border:1px solid rgba(6,182,212,0.3); border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:700; color:#06B6D4;">ANALYTICAL MART</div>
                    <div style="font-weight:700; color:{text_primary};">gold.revenue_mart</div>
                </div>
                <div style="background:rgba(6,182,212,0.12); border:1px solid rgba(6,182,212,0.3); border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:700; color:#06B6D4;">PERFORMANCE MART</div>
                    <div style="font-weight:700; color:{text_primary};">gold.driver_performance_mart</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Table Explorer Selectbox
    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Search', '#3B82F6', 18)} Interactive Table Explorer</div>""", unsafe_allow_html=True)
    selected_tbl = st.selectbox("Select Gold Table to Inspect", GOLD_TABLES, key="wh_table_sel")

    try:
        engine = get_engine()
        with engine.connect() as conn:
            cnt_val = conn.execute(text(f"SELECT COUNT(*) FROM gold.{selected_tbl}")).scalar()
            col_df = pd.read_sql_query(
                text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='gold' AND table_name='{selected_tbl}' ORDER BY ordinal_position;"),
                conn
            )
            sample_df = pd.read_sql_query(text(f"SELECT * FROM gold.{selected_tbl} LIMIT 20;"), conn)

        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Selected Table", f"gold.{selected_tbl}", "Database", "Gold Warehouse Schema", "#3B82F6")
        with c2:
            render_kpi_card("Row Count", f"{cnt_val:,}", "ChartColumn", "Total Table Records", "#10B981")
        with c3:
            render_kpi_card("Column Count", f"{len(col_df)}", "Workflow", "Total Table Attributes", "#8B5CF6")

        t1, t2 = st.tabs(["Sample Rows Preview", "Column Schema Definitions"])
        with t1:
            st.dataframe(sample_df, use_container_width=True, hide_index=True)
        with t2:
            st.dataframe(col_df, use_container_width=True, hide_index=True)

    except Exception as ex:
        st.error(f"Could not inspect table gold.{selected_tbl}: {ex}")

    st.divider()

    # Safe SQL Query Runner
    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Code', '#8B5CF6', 18)} Safe Read-Only SQL Query Runner</div>""", unsafe_allow_html=True)
    sql_input = st.text_area("SQL Query (Read-Only Gold Schema Only)", f"SELECT * FROM gold.{selected_tbl} LIMIT 50;", height=100, key="wh_sql_input")

    if st.button("Execute SQL Query", key="btn_exec_sql", type="primary"):
        try:
            df_res = execute_read_only_query(sql_input)
            st.success(f"Query executed successfully! Retrieved {len(df_res)} rows.")
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            st.download_button("Download Query Result CSV", df_res.to_csv(index=False), "query_result.csv", "text/csv")
        except Exception as ex:
            st.error(f"SQL Execution Error: {ex}")
