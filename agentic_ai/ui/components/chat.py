import pandas as pd
import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.voice import generate_audio_reply
from agentic_ai.ui.components.charts import (
    render_area_chart,
    render_bar_chart,
    render_horizontal_bar_chart,
    render_donut_chart,
    render_scatter_chart,
)

AGENT_BADGES = {
    "data_agent": ("Database", "🗄 DATA AGENT", "#3B82F6"),
    "support_agent": ("BookOpen", "📚 SUPPORT AGENT", "#10B981"),
    "ml_agent": ("BrainCircuit", "🧠 ML AGENT", "#F59E0B"),
    "report_agent": ("FileText", "📄 REPORT AGENT", "#6366F1"),
    "general": ("Bot", "✦ GENERAL AI", "#8B5CF6"),
    "multi_agent": ("Network", "◉ MULTI-AGENT", "#EC4899"),
}


def get_agent_badge_html(route: str) -> tuple[str, str]:
    """Return active agent badge HTML and theme color string."""
    icon_name, label, color = AGENT_BADGES.get(route, ("Bot", route.upper(), "#8B5CF6"))
    badge_html = (
        f'<div class="ai-agent-badge" style="display:inline-flex; align-items:center; gap:6px; background:{color}18; color:{color}; border:1px solid {color}44; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px; margin-bottom:8px;">'
        f'<span>{label}</span>'
        f'</div>'
    )
    return badge_html, color


def get_contextual_followups(route: str = "general", intent: str = "", question: str = "") -> list[str]:
    """Generate 2-3 dynamic contextual follow-up query suggestions based on agent route and intent."""
    q_lower = question.lower() if question else ""
    r_lower = route.lower() if route else "general"

    if "driver" in q_lower or r_lower == "ml_agent":
        return [
            "Why is this driver high risk?",
            "Compare driver with fleet average",
            "Show top 5 revenue drivers",
        ]
    elif "revenue" in q_lower or "kpi" in q_lower or r_lower == "data_agent":
        return [
            "Compare weekday vs weekend performance",
            "Show top revenue drivers",
            "Analyse revenue trend over time",
        ]
    elif "sop" in q_lower or "policy" in q_lower or r_lower == "support_agent":
        return [
            "What is the vehicle accident escalation SOP?",
            "Show driver safety policy",
            "View support guidelines",
        ]
    elif r_lower == "report_agent":
        return [
            "Show executive KPIs",
            "Analyse revenue trend over time",
            "Show top 5 drivers by revenue",
        ]
    else:
        return [
            "What are the executive KPIs?",
            "Who are the top 5 drivers by revenue?",
            "Compare weekday vs weekend performance",
        ]


def render_auto_visualization(df: pd.DataFrame):
    """Automatically select meaningful visualization based on returned dataframe structure."""
    if df.empty:
        st.info("No data available for visualization.")
        return

    if len(df) == 1:
        st.info("Single-row metric summary is displayed in Data Table.")
        return

    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    str_cols = df.select_dtypes(include=["object", "string", "datetime"]).columns.tolist()

    x_col = str_cols[0] if str_cols else cols[0]
    y_col = numeric_cols[0] if numeric_cols else cols[1 if len(cols) > 1 else 0]

    if any(k in x_col.lower() for k in ("date", "time", "day", "dt", "key")):
        render_area_chart(df, x_col=x_col, y_col=y_col, height=260)
    elif any(k in x_col.lower() for k in ("name", "driver", "city", "rank", "id")):
        render_horizontal_bar_chart(df, y_col=x_col, x_col=y_col, height=240)
    elif len(df) <= 6 and numeric_cols:
        render_donut_chart(df, category_col=x_col, value_col=y_col, height=240)
    elif numeric_cols:
        render_bar_chart(df, x_col=x_col, y_col=y_col, height=260)
    elif len(numeric_cols) >= 2:
        render_scatter_chart(df, x_col=numeric_cols[0], y_col=numeric_cols[1], height=260)
    else:
        st.info("Chart view is not available for this data shape.")


def render_response_card(result: dict, index: int = 0) -> str | None:
    """Render structured SaaS assistant response card with agent badge, answer text, response tabs, action bar, and follow-up chips."""
    route = result.get("route", "general")
    badge_html, agent_color = get_agent_badge_html(route)

    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    card_bg = "#151D2F" if is_dark else "#FFFFFF"
    card_border = "rgba(148,163,184,0.14)" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    st.markdown(f"""
        <div class="ai-agent-message" style="background:{card_bg}; border-left:4px solid {agent_color}; border-top:1px solid {card_border}; border-right:1px solid {card_border}; border-bottom:1px solid {card_border}; border-radius:12px; padding:16px; margin-bottom:14px; box-shadow:0 4px 16px rgba(0,0,0,0.06);">
            {badge_html}
        </div>
    """, unsafe_allow_html=True)

    answer_text = result.get("answer", "")
    st.markdown(answer_text)

    # Response Action Bar (🔊 Listen | 📋 Copy | ⬇ Export)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    has_data = result.get("data") is not None and isinstance(result["data"], pd.DataFrame) and not result["data"].empty

    act_cols = st.columns([2, 2, 2, 4])

    with act_cols[0]:
        if answer_text and st.session_state.get("enable_voice", True):
            if st.button("🔊 Listen", key=f"btn_listen_audio_{index}", help="Listen to a spoken summary of key takeaways."):
                st.session_state[f"audio_reply_bytes_{index}"] = generate_audio_reply(answer_text)

    with act_cols[1]:
        if st.button("📋 Copy Text", key=f"btn_copy_text_{index}", help="Copy response to clipboard"):
            st.toast("Response text copied to clipboard!", icon="📋")

    with act_cols[2]:
        if has_data:
            csv_data = result["data"].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇ Export CSV",
                data=csv_data,
                file_name=f"query_result_{index}.csv",
                mime="text/csv",
                key=f"dl_csv_bar_{index}"
            )

    # Render TTS Audio Player if generated
    if f"audio_reply_bytes_{index}" in st.session_state:
        audio_bytes = st.session_state[f"audio_reply_bytes_{index}"]
        if audio_bytes:
            st.caption("🔊 **Spoken Summary**")
            st.audio(audio_bytes, format="audio/mp3", autoplay=False)
        else:
            st.info("Voice playback is temporarily unavailable.")

    st.divider()

    # Secondary Data & Metadata Tabs
    show_sql = st.session_state.get("display_sql", True)
    show_trace = st.session_state.get("display_trace", True)
    show_sources = st.session_state.get("display_sources", True)

    has_sql = bool(result.get("sql")) and show_sql
    has_sources = bool(result.get("sources")) and show_sources
    has_trace = bool(result.get("trace_steps")) and show_trace

    tab_titles = ["Answer"]
    if has_data:
        tab_titles.append("Data Table")
        tab_titles.append("Visualization")
    if has_sql:
        tab_titles.append("Generated SQL")
    if has_sources:
        tab_titles.append("RAG Evidence")
    if has_trace:
        tab_titles.append("Execution Trace")

    tabs = st.tabs(tab_titles)
    tab_idx = 0

    # Answer / Takeaways Tab
    with tabs[tab_idx]:
        tab_idx += 1
        st.caption("🔍 Analytical Metadata & Agent Routing:")
        st.write(f"• **Agent Route:** `{result.get('route', 'general')}` | **Intent:** `{result.get('intent', 'N/A')}`")
        st.write(f"• **Routing Rationale:** {result.get('routing_reason', 'Multi-Agent Supervisor Routing')}")
        if result.get("insights"):
            st.info(f"💡 **Business Insight:** {result['insights']}")
        if result.get("recommendations"):
            st.success(f"🎯 **Recommended Action:** {result['recommendations']}")

    # Data Table Tab
    if has_data:
        df = result["data"]
        with tabs[tab_idx]:
            tab_idx += 1
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Auto Visualization Tab
        with tabs[tab_idx]:
            tab_idx += 1
            render_auto_visualization(df)

    # Generated SQL Tab
    if has_sql:
        with tabs[tab_idx]:
            tab_idx += 1
            st.code(result["sql"], language="sql")
            st.caption(f"**Tables Inspected:** `{result.get('tables_used', ['gold.*'])}` | **Security:** Read-Only Schema Enforced")

    # RAG Sources / Evidence Tab
    if has_sources:
        with tabs[tab_idx]:
            tab_idx += 1
            for src in result.get("sources", []):
                st.write(f"📄 **Source Document:** `{src}`")

    # Agent Execution Trace Tab
    if has_trace:
        with tabs[tab_idx]:
            tab_idx += 1
            for step in result.get("trace_steps", []):
                st.write(f"• `{step}`")
            st.caption(f"⏱️ **Execution Duration:** `{result.get('execution_time_ms', 0)} ms`")

    # Dynamic Contextual Follow-up Chips
    followup_queries = get_contextual_followups(route=route, intent=result.get("intent", ""), question=answer_text)
    if followup_queries:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#94A3B8; margin-bottom:6px;'>SUGGESTED FOLLOW-UP QUESTIONS:</div>", unsafe_allow_html=True)
        
        f_cols = st.columns(len(followup_queries))
        for idx_f, f_q in enumerate(followup_queries):
            with f_cols[idx_f]:
                if st.button(f"💬 {f_q}", key=f"btn_followup_{index}_{idx_f}", use_container_width=True):
                    return f_q

    return None
