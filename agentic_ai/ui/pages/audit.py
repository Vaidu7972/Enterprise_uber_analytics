import pandas as pd
import streamlit as st
from agentic_ai.memory.persistent_memory import get_recent_audit_logs
from agentic_ai.ui.styles.icons import get_icon_svg


def render_audit_page():
    """Render SaaS Audit Logs Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Audit Logs</h1>
            <p>System compliance audit trail for intent classification, SQL query execution, and management decisions.</p>
        </div>
    """, unsafe_allow_html=True)

    logs = get_recent_audit_logs()
    if logs:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ClipboardList', '#3B82F6', 18)} Compliance Audit Logs</div>""", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
    else:
        st.info("No compliance audit records logged yet.")
