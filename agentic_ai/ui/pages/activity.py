import pandas as pd
import streamlit as st
from agentic_ai.memory.persistent_memory import get_recent_audit_logs
from agentic_ai.ui.styles.icons import get_icon_svg


def render_activity_page():
    """Render SaaS Agent Activity Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Agent Activity</h1>
            <p>Operational execution activity table across Data, Support, ML, and Multi-Agent routes.</p>
        </div>
    """, unsafe_allow_html=True)

    logs = get_recent_audit_logs()
    if logs:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Activity', '#3B82F6', 18)} Recent Agent Activity Logs</div>""", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
    else:
        st.info("No agent activity records logged yet.")
