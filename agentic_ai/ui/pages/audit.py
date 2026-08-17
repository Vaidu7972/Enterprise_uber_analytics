import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.memory.persistent_memory import get_recent_audit_logs, get_all_action_logs
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_status_pill

def render_audit_page():
    """Render SaaS Audit Logs Page with separated compliance audit tabs."""
    st.markdown("""
        <div class="page-header">
            <h1>Audit Logs & Compliance</h1>
            <p>System compliance audit trail for ETL batch ingestion, agent intent routing, and management governance decisions.</p>
        </div>
    """, unsafe_allow_html=True)

    t_agent, t_action, t_etl = st.tabs(["🤖 Agent Audit Logs", "📋 Action Governance Audit", "⚙️ ETL Ingestion Audit"])

    with t_agent:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Bot', '#3B82F6', 18)} Agent Intent & Routing Compliance Audit</div>""", unsafe_allow_html=True)
        agent_logs = get_recent_audit_logs()
        if agent_logs:
            df_ag = pd.DataFrame(agent_logs)
            if "status" in df_ag.columns:
                df_ag["status_pill"] = df_ag["status"].apply(render_status_pill)
            st.dataframe(df_ag, use_container_width=True, hide_index=True)
            st.download_button("Download Agent Audit CSV", df_ag.to_csv(index=False), "agent_audit_logs.csv", "text/csv")
        else:
            st.info("No agent audit records logged yet.")

    with t_action:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ClipboardList', '#10B981', 18)} Human-in-the-Loop Action Governance Log</div>""", unsafe_allow_html=True)
        action_logs = get_all_action_logs()
        if action_logs:
            df_act = pd.DataFrame(action_logs)
            if "status" in df_act.columns:
                df_act["status_pill"] = df_act["status"].apply(render_status_pill)
            st.dataframe(df_act, use_container_width=True, hide_index=True)
            st.download_button("Download Action Audit CSV", df_act.to_csv(index=False), "action_audit_logs.csv", "text/csv")
        else:
            st.info("No action audit records stored in Gold schema yet.")

    with t_etl:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Workflow', '#8B5CF6', 18)} Airflow Pipeline ETL Execution Log</div>""", unsafe_allow_html=True)
        try:
            engine = get_engine()
            with engine.connect() as conn:
                df_etl = pd.read_sql_query(text("SELECT batch_id, pipeline_name, task_name, target_table, status, rows_read, rows_inserted, last_watermark, start_time, end_time FROM audit.etl_batch_log ORDER BY batch_id DESC LIMIT 50;"), conn)
            if not df_etl.empty:
                df_etl["status_pill"] = df_etl["status"].apply(render_status_pill)
                st.dataframe(df_etl, use_container_width=True, hide_index=True)
                st.download_button("Download ETL Log CSV", df_etl.to_csv(index=False), "etl_batch_logs.csv", "text/csv")
            else:
                st.info("No ETL batch records found.")
        except Exception as ex:
            st.error(f"Could not load ETL audit logs: {ex}")
