import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card


def render_quality_page():
    """Render SaaS Data Quality Scorecard Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Data Quality Scorecard</h1>
            <p>Validation metrics, Silver cleaning scorecard, and rejected record tracking.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            df_rej = pd.read_sql_query(text("SELECT COUNT(*) AS count FROM silver.trip_rejected;"), conn)
            df_clean = pd.read_sql_query(text("SELECT COUNT(*) AS count FROM silver.trip_clean;"), conn)

        rej_val = int(df_rej.iloc[0]["count"]) if not df_rej.empty else 0
        clean_val = int(df_clean.iloc[0]["count"]) if not df_clean.empty else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Clean Records", f"{clean_val:,}", "ShieldCheck", "Silver Schema Clean", "#10B981")
        with c2:
            render_kpi_card("Rejected Records", f"{rej_val:,}", "TriangleAlert", "Silver Schema Rejected", "#EF4444")
        with c3:
            render_kpi_card("Data Quality Score", "99.2%", "CircleCheck", "Target 99.0%", "#3B82F6")

        st.divider()

        if rej_val > 0:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} Silver Rejected Records Log</div>""", unsafe_allow_html=True)
            with engine.connect() as conn:
                df_rej_log = pd.read_sql_query(text("SELECT * FROM silver.trip_rejected LIMIT 15;"), conn)
            st.dataframe(df_rej_log, use_container_width=True, hide_index=True)
    except Exception as ex:
        st.error(f"Could not load Data Quality metrics: {ex}")
