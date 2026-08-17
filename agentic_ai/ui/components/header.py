import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.health import (
    check_postgres_connection,
    check_gold_schema,
    check_gemini_configuration,
    check_ml_model,
    check_vector_store,
    check_pipeline_health,
)

def render_saas_header():
    """Render slim SaaS top bar header with real connectivity and system status checks."""
    db_connected = check_postgres_connection()
    gold_ready = check_gold_schema() if db_connected else False
    gemini_online = check_gemini_configuration()
    ml_ready = check_ml_model() if db_connected else False
    rag_ready = check_vector_store()

    pipeline_info = check_pipeline_health()
    last_refresh_str = pipeline_info.get("last_refresh", "Live")

    # Status Pills HTML
    db_pill = f"""<span class="status-pill status-pill-green">{get_icon_svg('CircleCheck', '#10B981', 14)} PostgreSQL Connected</span>""" if db_connected else f"""<span class="status-pill status-pill-red">{get_icon_svg('CircleX', '#EF4444', 14)} PostgreSQL Offline</span>"""
    gold_pill = f"""<span class="status-pill status-pill-purple">{get_icon_svg('Database', '#8B5CF6', 14)} Gold Warehouse Ready</span>""" if gold_ready else f"""<span class="status-pill status-pill-red">{get_icon_svg('CircleX', '#EF4444', 14)} Gold Unchecked</span>"""
    gemini_pill = f"""<span class="status-pill status-pill-blue">{get_icon_svg('Bot', '#3B82F6', 14)} Gemini Online</span>""" if gemini_online else f"""<span class="status-pill status-pill-amber">{get_icon_svg('TriangleAlert', '#F59E0B', 14)} Gemini Key Missing</span>"""
    ml_pill = f"""<span class="status-pill status-pill-green">{get_icon_svg('BrainCircuit', '#10B981', 14)} ML Model Ready</span>""" if ml_ready else f"""<span class="status-pill status-pill-amber">{get_icon_svg('Clock', '#F59E0B', 14)} ML Model Offline</span>"""
    rag_pill = f"""<span class="status-pill status-pill-blue">{get_icon_svg('BookOpen', '#06B6D4', 14)} RAG Index Ready</span>""" if rag_ready else f"""<span class="status-pill status-pill-amber">{get_icon_svg('Clock', '#F59E0B', 14)} RAG Offline</span>"""
    
    refresh_pill = f"""<span class="status-pill" style="background:rgba(148,163,184,0.12); color:#94A3B8;">{get_icon_svg('RotateCw', '#94A3B8', 14)} Refreshed {last_refresh_str}</span>"""
    clock_pill = f"""<span class="status-pill" style="background:rgba(6,182,212,0.14); color:#06B6D4; border-color:rgba(6,182,212,0.35); font-weight:700; font-family: monospace; font-size:0.78rem;">{get_icon_svg('Clock', '#06B6D4', 14)} <span id="live-realtime-clock">Syncing...</span><img src="x" onerror="if(!window.uberOpsClockTimer){{window.uberOpsClockTimer=setInterval(function(){{var el=document.getElementById('live-realtime-clock');if(el){{var now=new Date();el.innerText=now.toLocaleTimeString('en-US',{{hour12:true,hour:'2-digit',minute:'2-digit',second:'2-digit'}});}}}},1000);}} var el=document.getElementById('live-realtime-clock');if(el){{var now=new Date();el.innerText=now.toLocaleTimeString('en-US',{{hour12:true,hour:'2-digit',minute:'2-digit',second:'2-digit'}});}}" style="display:none;" /></span>"""

    is_dark = (st.session_state.get("theme_mode", "dark") == "dark")
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    topbar_html = (
        f'<div class="saas-topbar">'
        f'<div class="saas-topbar-title">'
        f'{get_icon_svg("Activity", "#3B82F6", 24)}'
        f'<span style="color:{title_color};">UberOps AI</span>'
        f'<span style="font-size:0.85rem; font-weight:400; color:{sub_color};">| Enterprise Mobility Intelligence</span>'
        f'</div>'
        f'<div class="saas-topbar-badges">'
        f'{gold_pill}'
        f'{db_pill}'
        f'{gemini_pill}'
        f'{ml_pill}'
        f'{rag_pill}'
        f'{refresh_pill}'
        f'{clock_pill}'
        f'</div>'
        f'</div>'
    )
    st.markdown(topbar_html, unsafe_allow_html=True)
