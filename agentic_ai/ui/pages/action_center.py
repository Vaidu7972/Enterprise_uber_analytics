import pandas as pd
import streamlit as st
from agentic_ai.memory.persistent_memory import get_recent_audit_logs
from agentic_ai.ui.styles.icons import get_icon_svg


def render_action_center_page():
    """Render SaaS Action Center Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Action Center</h1>
            <p>Human-in-the-loop pending, approved, and rejected operational recommendations.</p>
        </div>
    """, unsafe_allow_html=True)

    logs = get_recent_audit_logs()
    if logs:
        df_actions = pd.DataFrame(logs)
        if "action_recommended" in df_actions.columns:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ListChecks', '#3B82F6', 18)} Audit Recommended Actions</div>""", unsafe_allow_html=True)
            st.dataframe(df_actions[["timestamp", "agent", "route", "action_recommended", "approval_status"]], use_container_width=True, hide_index=True)
        else:
            st.info("No management actions currently logged.")
    else:
        st.info("No operational actions logged yet.")
