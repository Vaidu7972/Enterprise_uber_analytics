import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg


def render_kpi_card(title: str, value: str, icon_name: str = "TrendingUp", subtext: str = "", icon_color: str = "#3B82F6"):
    """Render structured SaaS KPI metric card."""
    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span>{title}</span>
            {get_icon_svg(icon_name, icon_color, 18)}
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_starter_card(title: str, description: str, icon_name: str, icon_color: str = "#60A5FA"):
    """Render AI starter question card."""
    return f"""
    <div class="starter-card">
        <div style="display:flex; align-items:center; gap:8px;">
            {get_icon_svg(icon_name, icon_color, 20)}
            <h4 style="margin:0; font-size:0.95rem; font-weight:700; color:#F8FAFC;">{title}</h4>
        </div>
        <p style="margin:6px 0 0 0; font-size:0.8rem; color:#94A3B8;">{description}</p>
    </div>
    """


def render_status_pill(status: str) -> str:
    """Render status pill pill badge HTML."""
    status_lower = status.lower()
    if status_lower in ("completed", "success", "ready", "online"):
        return f"""<span class="status-pill status-pill-green">{get_icon_svg('CircleCheck', '#4ADE80', 14)} {status}</span>"""
    elif status_lower in ("running", "processing", "in progress"):
        return f"""<span class="status-pill status-pill-blue">{get_icon_svg('RefreshCw', '#60A5FA', 14)} {status}</span>"""
    elif status_lower in ("failed", "error", "offline"):
        return f"""<span class="status-pill" style="background:rgba(239,68,68,0.12); color:#FCA5A5; border-color:rgba(239,68,68,0.25);">{get_icon_svg('CircleX', '#FCA5A5', 14)} {status}</span>"""
    else:
        return f"""<span class="status-pill" style="background:rgba(234,179,8,0.12); color:#FDE047; border-color:rgba(234,179,8,0.25);">{get_icon_svg('Clock', '#FDE047', 14)} {status}</span>"""
