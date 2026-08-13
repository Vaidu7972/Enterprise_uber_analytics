import pandas as pd
import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.voice import render_tts_audio_player


AGENT_BADGES = {
    "data_agent": ("Database", "DATA AGENT", "#3B82F6"),
    "support_agent": ("BookOpen", "SUPPORT AGENT", "#10B981"),
    "ml_agent": ("BrainCircuit", "ML AGENT", "#F59E0B"),
    "report_agent": ("FileText", "REPORT AGENT", "#8B5CF6"),
    "general": ("Bot", "GENERAL AI", "#64748B"),
    "multi_agent": ("Network", "MULTI-AGENT", "#EC4899"),
}


def get_agent_badge_html(route: str) -> str:
    """Return active agent Lucide SVG badge HTML."""
    icon_name, label, color = AGENT_BADGES.get(route, ("Bot", route.upper(), "#64748B"))
    return f"""
    <div class="agent-badge" style="background:rgba(59,130,246,0.12); color:{color}; border-color:{color}44;">
        {get_icon_svg(icon_name, color, 14)}
        <span>{label}</span>
    </div>
    """


def render_response_card(result: dict, index: int = 0):
    """
    Render structured SaaS assistant response card with tabs:
    [Answer | Data | Visualization | SQL | Agent Trace]
    """
    route = result.get("route", "general")
    st.markdown(get_agent_badge_html(route), unsafe_allow_html=True)

    # 1. Main Business Answer
    st.markdown(result.get("answer", ""))

    # TTS Audio Player
    if result.get("answer"):
        render_tts_audio_player(result["answer"], key_suffix=f"res_{index}")

    st.divider()

    # 2. Response Tabs
    has_data = result.get("data") is not None and isinstance(result["data"], pd.DataFrame) and not result["data"].empty
    has_sql = bool(result.get("sql"))
    has_trace = bool(result.get("trace_steps"))

    tab_titles = ["Answer Summary"]
    if has_data:
        tab_titles.append("Data Table")
        tab_titles.append("Visualization")
    if has_sql:
        tab_titles.append("SQL Query")
    if has_trace:
        tab_titles.append("Agent Trace")

    tabs = st.tabs(tab_titles)
    tab_idx = 0

    # Answer Summary Tab
    with tabs[tab_idx]:
        tab_idx += 1
        st.caption("🔍 Key Analytical Takeaways:")
        if result.get("insights"):
            st.info(f"**Business Insight:** {result['insights']}")
        if result.get("recommendations"):
            st.success(f"**Recommended Action:** {result['recommendations']}")
        if not result.get("insights") and not result.get("recommendations"):
            st.write("Response generated directly from PostgreSQL Gold data and AI tools.")

    # Data Table Tab
    if has_data:
        df = result["data"]
        with tabs[tab_idx]:
            tab_idx += 1
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV Data",
                data=csv_data,
                file_name=f"query_result_{index}.csv",
                mime="text/csv",
                key=f"dl_csv_{index}"
            )

        # Visualization Tab
        with tabs[tab_idx]:
            tab_idx += 1
            if len(df) > 1:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    st.line_chart(df[numeric_cols], use_container_width=True)
                else:
                    st.info("Chart view is not available for this data shape.")
            else:
                st.info("Single-row metric results are best viewed in Answer Summary.")

    # SQL Query Tab
    if has_sql:
        with tabs[tab_idx]:
            tab_idx += 1
            st.code(result["sql"], language="sql")
            st.caption(f"**Tables Inspected:** `{result.get('tables_used', [])}` | **Security:** Read-Only Gold Schema")

    # Agent Trace Tab
    if has_trace:
        with tabs[tab_idx]:
            tab_idx += 1
            for step in result.get("trace_steps", []):
                st.write(f"• `{step}`")
            st.caption(f"⏱️ **Execution Duration:** `{result.get('execution_time_ms', 0)} ms`")
