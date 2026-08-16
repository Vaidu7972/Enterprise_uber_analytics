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
        df_logs = pd.DataFrame(logs)
        total_q = len(df_logs)
        success_q = len(df_logs[df_logs["status"].str.lower().isin(["success", "completed", "ok"])])
        success_rate = round((success_q / total_q) * 100, 1) if total_q > 0 else 100.0
        top_agent = df_logs["agent"].mode().iloc[0] if not df_logs["agent"].empty else "Multi-Agent"

        from agentic_ai.ui.components.cards import render_kpi_card
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Questions Processed", f"{total_q}", "MessageSquare", "Audit Log Total", "#3B82F6")
        with m2:
            render_kpi_card("Primary Agent", f"{top_agent}", "Bot", "Highest Frequency", "#8B5CF6")
        with m3:
            render_kpi_card("Execution Success Rate", f"{success_rate}%", "ShieldCheck", "Zero Failures", "#10B981")
        with m4:
            render_kpi_card("Audit Records", f"{len(df_logs)}", "ClipboardList", "PostgreSQL Gold", "#F59E0B")

        st.divider()
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Activity', '#3B82F6', 18)} Agent Activity Execution Trail</div>""", unsafe_allow_html=True)
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
    else:
        st.info("No agent activity records logged in PostgreSQL Gold schema yet.")
