import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg


def render_settings_page():
    """Render SaaS Platform Settings Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Platform Settings</h1>
            <p>Configure agent execution displays, query limits, voice input, and system preferences.</p>
        </div>
    """, unsafe_allow_html=True)

    if "display_sql" not in st.session_state:
        st.session_state.display_sql = True
    if "display_trace" not in st.session_state:
        st.session_state.display_trace = True
    if "enable_voice" not in st.session_state:
        st.session_state.enable_voice = True
    if "result_limit" not in st.session_state:
        st.session_state.result_limit = 200

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Settings', '#3B82F6', 18)} Agent Display Preferences</div>""", unsafe_allow_html=True)
    
    st.session_state.display_sql = st.checkbox("Display Generated Read-Only SQL Queries", value=st.session_state.display_sql)
    st.session_state.display_trace = st.checkbox("Display Agent Execution Traces", value=st.session_state.display_trace)
    st.session_state.enable_voice = st.checkbox("Enable Web Speech API Microphone Voice Input", value=st.session_state.enable_voice)
    st.session_state.result_limit = st.number_input("Max Query Result Row Limit", min_value=10, max_value=1000, value=st.session_state.result_limit)

    st.success("Session preferences saved!")
