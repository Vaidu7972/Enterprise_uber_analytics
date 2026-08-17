import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg

def render_kpi_card(
    title: str,
    value: str,
    icon_name: str = "TrendingUp",
    subtext: str = "",
    icon_color: str = "#3B82F6",
    change_text: str = None,
    is_positive: bool = True,
):
    """Render high-end SaaS KPI metric card matching modern UI reference standards."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"

    badge_bg = f"{icon_color}1F"  # 12% opacity
    badge_border = f"{icon_color}40"  # 25% opacity

    trend_html = ""
    if change_text:
        if "comparison" in change_text.lower() or "baseline" in change_text.lower() or "n/a" in change_text.lower():
            trend_html = (
                f'<span style="font-size:0.72rem; font-weight:600; color:#94A3B8; '
                f'background:rgba(148,163,184,0.12); padding:2px 8px; border-radius:999px; '
                f'border:1px solid rgba(148,163,184,0.2);">{change_text}</span>'
            )
        else:
            trend_color = "#10B981" if is_positive else "#EF4444"
            trend_arrow = "↑" if is_positive else "↓"
            clean_text = change_text.lstrip("↑↓+- ").strip()
            trend_html = (
                f'<span style="font-size:0.75rem; font-weight:700; color:{trend_color}; '
                f'background:{trend_color}18; padding:2px 8px; border-radius:999px; '
                f'border:1px solid {trend_color}30;">{trend_arrow} {clean_text}</span>'
            )

    card_html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-header" style="display:flex; align-items:center; justify-content:space-between;">'
        f'<span style="font-weight:600; font-size:0.84rem; text-transform:none; letter-spacing:0.2px;">{title}</span>'
        f'<div style="width:34px; height:34px; border-radius:10px; background:{badge_bg}; border:1px solid {badge_border}; display:flex; align-items:center; justify-content:center;">'
        f'{get_icon_svg(icon_name, icon_color, 18)}'
        f'</div>'
        f'</div>'
        f'<div style="display:flex; align-items:baseline; justify-content:space-between; margin-top:8px;">'
        f'<div class="kpi-value" style="margin:0;">{value}</div>'
        f'{trend_html}'
        f'</div>'
        f'<div class="kpi-subtext" style="margin-top:4px;">{subtext}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_starter_card(title: str, description: str, icon_name: str, icon_color: str = "#3B82F6"):
    """Render AI starter question card."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    return (
        f'<div class="starter-card">'
        f'<div style="display:flex; align-items:center; gap:8px;">'
        f'<div style="width:28px; height:28px; border-radius:8px; background:{icon_color}1A; display:flex; align-items:center; justify-content:center;">'
        f'{get_icon_svg(icon_name, icon_color, 16)}'
        f'</div>'
        f'<h4 style="margin:0; font-size:0.92rem; font-weight:700; color:{title_color};">{title}</h4>'
        f'</div>'
        f'<p style="margin:6px 0 0 0; font-size:0.8rem; color:{sub_color};">{description}</p>'
        f'</div>'
    )


def render_status_pill(status: str) -> str:
    """Render status pill badge HTML."""
    status_str = str(status) if status is not None else "Unknown"
    status_lower = status_str.lower()

    if status_lower in ("completed", "success", "ready", "online", "active", "approved", "low risk", "low"):
        return f'<span class="status-pill status-pill-green">{get_icon_svg("CircleCheck", "#10B981", 14)} {status_str}</span>'
    elif status_lower in ("running", "processing", "in progress", "pending"):
        return f'<span class="status-pill status-pill-blue">{get_icon_svg("RotateCw", "#3B82F6", 14)} {status_str}</span>'
    elif status_lower in ("failed", "error", "offline", "high risk", "high", "rejected", "critical"):
        return f'<span class="status-pill status-pill-red">{get_icon_svg("CircleX", "#EF4444", 14)} {status_str}</span>'
    else:
        return f'<span class="status-pill status-pill-amber">{get_icon_svg("Clock", "#F59E0B", 14)} {status_str}</span>'
