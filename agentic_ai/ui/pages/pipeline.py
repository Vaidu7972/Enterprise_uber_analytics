import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_status_pill


def render_pipeline_page():
    """Render SaaS Pipeline Health Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Pipeline Health</h1>
            <p>Airflow DAG execution status, batch timing, and ingestion audit log from audit.etl_batch_log.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            df_etl = pd.read_sql_query(text("SELECT batch_id, task_name, target_table, status, rows_read, rows_inserted, rows_updated, rows_rejected, last_watermark, start_time, end_time FROM audit.etl_batch_log ORDER BY batch_id DESC LIMIT 20;"), conn)

        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Workflow', '#3B82F6', 18)} Airflow DAG Batch Execution Log</div>""", unsafe_allow_html=True)
        st.dataframe(df_etl, use_container_width=True, hide_index=True)
    except Exception as ex:
        st.error(f"Could not load Pipeline Health data: {ex}")
