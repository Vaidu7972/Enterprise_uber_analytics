import os
import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.health import (
    check_postgres_connection,
    check_gold_schema,
    check_gemini_configuration,
    check_ml_model,
    check_vector_store,
    check_pipeline_health,
)

def render_settings_page():
    """Render Enterprise Platform Settings Page with clear tabbed configuration workspace."""
    st.markdown("""
        <div class="page-header">
            <h1>Platform Settings</h1>
            <p>Configure interface appearance, AI assistant behavior, query parameters, governance controls, and view system status.</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize Session State Defaults
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    if "display_sql" not in st.session_state:
        st.session_state.display_sql = True
    if "display_trace" not in st.session_state:
        st.session_state.display_trace = True
    if "display_sources" not in st.session_state:
        st.session_state.display_sources = True
    if "display_reason" not in st.session_state:
        st.session_state.display_reason = True
    if "enable_voice" not in st.session_state:
        st.session_state.enable_voice = True
    if "voice_lang" not in st.session_state:
        st.session_state.voice_lang = "en-IN"
    if "result_limit" not in st.session_state:
        st.session_state.result_limit = 200
    if "analytics_scope" not in st.session_state:
        st.session_state.analytics_scope = "30 Days"
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False
    if "confirm_approval" not in st.session_state:
        st.session_state.confirm_approval = True
    if "require_rejection_reason" not in st.session_state:
        st.session_state.require_rejection_reason = True

    t_app, t_ai, t_data, t_gov, t_sys, t_about = st.tabs([
        "🎨 Appearance",
        "🤖 AI Assistant",
        "📊 Data & Query",
        "🛡️ Governance",
        "🔌 System Status",
        "ℹ️ About"
    ])

    # TAB A: Appearance
    with t_app:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('SlidersHorizontal', '#3B82F6', 18)} Theme & Display Preferences</div>""", unsafe_allow_html=True)
        
        curr_theme = st.session_state.theme_mode
        new_theme = st.radio("Active Theme Mode", ["dark", "light"], index=0 if curr_theme == "dark" else 1, horizontal=True, key="set_theme_radio")
        if new_theme != curr_theme:
            st.session_state.theme_mode = new_theme
            st.rerun()

        st.selectbox("Accent Color System", ["Primary Blue (#3B82F6)", "Violet AI (#8B5CF6)", "Cyan Telemetry (#06B6D4)", "Emerald Success (#10B981)"], key="set_accent_color")
        st.selectbox("Layout Density", ["Comfortable Enterprise", "Compact High-Density"], key="set_density")
        st.checkbox("Reduced Motion / Micro-Animations", value=False, key="set_reduced_motion")
        st.checkbox("High Contrast Mode", value=False, key="set_high_contrast")

    # TAB B: AI Assistant
    with t_ai:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Bot', '#8B5CF6', 18)} Multi-Agent Response Display Controls</div>""", unsafe_allow_html=True)
        
        st.session_state.display_sql = st.checkbox("Display Generated Read-Only Gold SQL Queries", value=st.session_state.display_sql)
        st.session_state.display_trace = st.checkbox("Display Multi-Agent Reasoning Execution Traces", value=st.session_state.display_trace)
        st.session_state.display_sources = st.checkbox("Display RAG Document Sources & Relevance Scores", value=st.session_state.display_sources)
        st.session_state.display_reason = st.checkbox("Display LangGraph Intent Routing Reasons", value=st.session_state.display_reason)
        st.session_state.enable_voice = st.checkbox("Enable Web Speech Microphone Voice Query Input", value=st.session_state.enable_voice)

        lang_opts = ["English (India) [en-IN]", "English (US) [en-US]", "English (UK) [en-GB]"]
        curr_lang = st.session_state.get("voice_lang", "en-IN")
        default_idx = 0 if "en-IN" in curr_lang else (1 if "en-US" in curr_lang else 2)
        
        sel_lang = st.selectbox("Voice Assistant Transcription Language", lang_opts, index=default_idx, key="set_voice_lang_select")
        if "en-IN" in sel_lang:
            st.session_state.voice_lang = "en-IN"
        elif "en-US" in sel_lang:
            st.session_state.voice_lang = "en-US"
        else:
            st.session_state.voice_lang = "en-GB"

    # TAB C: Data & Query
    with t_data:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Database', '#10B981', 18)} Warehouse Query Safety Parameters</div>""", unsafe_allow_html=True)
        
        st.session_state.result_limit = st.number_input("Max Read-Only Query Row Limit", min_value=10, max_value=1000, value=st.session_state.result_limit, step=10)
        st.session_state.analytics_scope = st.selectbox("Default Dashboard Scope", ["7 Days", "15 Days", "30 Days"], index=2)
        st.session_state.auto_refresh = st.checkbox("Enable Auto-Refresh Telemetry", value=st.session_state.auto_refresh)
        if st.session_state.auto_refresh:
            st.selectbox("Refresh Interval", ["30 Seconds", "60 Seconds", "5 Minutes"])

    # TAB D: Governance
    with t_gov:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ShieldCheck', '#F59E0B', 18)} Human-in-the-Loop Approval Safeguards</div>""", unsafe_allow_html=True)
        
        st.session_state.confirm_approval = st.checkbox("Require Explicit Confirmation Before Executing Actions", value=st.session_state.confirm_approval)
        st.session_state.require_rejection_reason = st.checkbox("Prompt Rejection Reason for Action Dismissal", value=st.session_state.require_rejection_reason)

    # TAB E: System Status (Read-Only)
    with t_sys:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Activity', '#06B6D4', 18)} Live Backend System Connectivity</div>""", unsafe_allow_html=True)
        
        db_ok = check_postgres_connection()
        gold_ok = check_gold_schema()
        gemini_ok = check_gemini_configuration()
        ml_ok = check_ml_model()
        rag_ok = check_vector_store()
        pipe_info = check_pipeline_health()

        s1, s2, s3 = st.columns(3)
        with s1:
            render_kpi_card("PostgreSQL Database", "Connected" if db_ok else "Offline", "Database", "localhost:5432 / uber_dw", "#10B981" if db_ok else "#EF4444")
        with s2:
            render_kpi_card("Gold Data Schema", "Ready" if gold_ok else "Unchecked", "ShieldCheck", "gold.kpi_summary & marts", "#3B82F6" if gold_ok else "#EF4444")
        with s3:
            render_kpi_card("Gemini 1.5 Flash", "Online" if gemini_ok else "Missing Key", "Bot", "Google AI LLM Engine", "#8B5CF6" if gemini_ok else "#F59E0B")

        s4, s5, s6 = st.columns(3)
        with s4:
            render_kpi_card("RandomForest ML Model", "Loaded" if ml_ok else "Offline", "BrainCircuit", "Driver Risk Scorer", "#10B981" if ml_ok else "#F59E0B")
        with s5:
            render_kpi_card("ChromaDB RAG Index", "Ready" if rag_ok else "Offline", "BookOpen", "uberops_docs Collection", "#06B6D4" if rag_ok else "#F59E0B")
        with s6:
            render_kpi_card("Airflow Incremental ETL", pipe_info.get("status", "N/A"), "Workflow", f"Watermark: {pipe_info.get('watermark', 'N/A')}", "#3B82F6")

        st.caption("🔒 All database credentials and API secrets remain safely masked from the interface.")

    # TAB F: About
    with t_about:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Bot', '#3B82F6', 20)} UberOps AI — Enterprise Mobility Intelligence</div>""", unsafe_allow_html=True)
        st.markdown("""
            **Version:** `2.4.0-enterprise`  
            **Architecture:** End-to-End Enterprise Data Warehouse & Agentic AI Decision Support System  
            
            **Technology Stack:**
            - **Core UI & Logic:** Python 3.12, Streamlit, HTML5, Vanilla CSS Design System
            - **Data Platform & Warehouse:** PostgreSQL 16 (Bronze → Silver → Gold Medallion Architecture), SQLAlchemy 2.0
            - **Orchestration & ETL:** Apache Airflow, Docker, Great Expectations
            - **AI Multi-Agent System:** LangGraph, Google Gemini 1.5 Flash API, ChromaDB Vector Store
            - **Predictive Analytics:** scikit-learn RandomForest Classifier, Altair Visualization Engine
            - **Reporting & Governance:** ReportLab PDF Engine, PostgreSQL Persistent Audit Logs
        """)

    st.toast("Settings updated!", icon="⚙️")
