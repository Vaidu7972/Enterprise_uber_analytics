import os
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.ui.styles.icons import get_icon_svg


def render_saas_header():
    """Render slim SaaS top bar header with live connectivity checks."""
    # 1. PostgreSQL Connection Check
    db_connected = False
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    # 2. Gold Schema Check
    gold_ready = False
    if db_connected:
        try:
            with get_engine().connect() as conn:
                res = conn.execute(text("SELECT COUNT(*) FROM gold.kpi_summary")).scalar()
                if res is not None and res > 0:
                    gold_ready = True
        except Exception:
            gold_ready = False

    # 3. Gemini API Check
    gemini_online = bool(os.getenv("GEMINI_API_KEY"))

    # 4. Warehouse Refresh Timestamp
    last_refresh_str = "Live"
    if db_connected:
        try:
            with get_engine().connect() as conn:
                row = conn.execute(
                    text("SELECT MAX(end_time) AS last_refresh FROM audit.etl_batch_log WHERE status = 'SUCCESS'")
                ).mappings().first()
                if row and row["last_refresh"]:
                    last_refresh_str = row["last_refresh"].strftime("%H:%M")
        except Exception:
            pass

    # Status Pills HTML
    db_pill = f"""<span class="status-pill status-pill-green">{get_icon_svg('CircleCheck', '#4ADE80', 14)} PostgreSQL Connected</span>""" if db_connected else f"""<span class="status-pill" style="background:rgba(239,68,68,0.12); color:#FCA5A5; border-color:rgba(239,68,68,0.3);">{get_icon_svg('CircleX', '#FCA5A5', 14)} PostgreSQL Offline</span>"""
    gold_pill = f"""<span class="status-pill status-pill-purple">{get_icon_svg('Database', '#C084FC', 14)} Gold Layer Ready</span>""" if gold_ready else f"""<span class="status-pill" style="background:rgba(239,68,68,0.12); color:#FCA5A5;">{get_icon_svg('CircleX', '#FCA5A5', 14)} Gold Layer Unchecked</span>"""
    gemini_pill = f"""<span class="status-pill status-pill-blue">{get_icon_svg('Bot', '#60A5FA', 14)} Gemini Online</span>""" if gemini_online else f"""<span class="status-pill" style="background:rgba(234,179,8,0.12); color:#FDE047;">{get_icon_svg('TriangleAlert', '#FDE047', 14)} Key Missing</span>"""
    refresh_pill = f"""<span class="status-pill" style="background:rgba(148,163,184,0.12); color:#94A3B8;">{get_icon_svg('Clock', '#94A3B8', 14)} Refreshed {last_refresh_str}</span>"""

    topbar_html = f"""
    <div class="saas-topbar">
        <div class="saas-topbar-title">
            {get_icon_svg('Activity', '#3B82F6', 22)}
            <span>UberOps AI</span>
            <span style="font-size:0.85rem; font-weight:400; color:#94A3B8;">| Enterprise Mobility Decision Support</span>
        </div>
        <div class="saas-topbar-badges">
            {gold_pill}
            {db_pill}
            {gemini_pill}
            {refresh_pill}
        </div>
    </div>
    """
    st.markdown(topbar_html, unsafe_allow_html=True)
