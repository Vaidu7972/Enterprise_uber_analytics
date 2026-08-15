import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg

SAAS_DARK_CSS = """
<style>
/* Global SaaS Workspace Theme - Dark Mode */
.stApp {
    background-color: #0B101D;
    color: #F8FAFC;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

header[data-testid="stHeader"] {
    background-color: rgba(11, 16, 29, 0.85);
    backdrop-filter: blur(8px);
}

section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid rgba(148, 163, 184, 0.12) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Sidebar Navigation Buttons in Dark Mode */
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(30, 41, 59, 0.7) !important;
    color: #E2E8F0 !important;
    border: 1px solid rgba(148, 163, 184, 0.16) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] button:hover,
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(51, 65, 85, 0.8) !important;
    color: #F8FAFC !important;
    border-color: rgba(96, 165, 250, 0.3) !important;
}

section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[type="primary"] {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    font-weight: 700 !important;
}

/* Main Content Buttons in Dark Mode */
div[data-testid="stMain"] button,
div[data-testid="stMain"] .stButton > button {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25) !important;
}

div[data-testid="stMain"] button:hover,
div[data-testid="stMain"] .stButton > button:hover {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border-color: #1D4ED8 !important;
}

/* Main Content Text Inputs in Dark Mode */
div[data-testid="stMain"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="input"],
div[data-baseweb="input"] > div {
    background-color: #151D2F !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 8px !important;
}

.saas-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #151D2F;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 12px;
    padding: 10px 20px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.saas-topbar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.15rem;
    font-weight: 700;
    color: #F8FAFC;
}

.saas-topbar-badges {
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

.status-pill-green {
    background: rgba(34, 197, 94, 0.12);
    color: #4ADE80;
    border-color: rgba(74, 222, 128, 0.25);
}

.status-pill-blue {
    background: rgba(59, 130, 246, 0.12);
    color: #60A5FA;
    border-color: rgba(96, 165, 250, 0.25);
}

.status-pill-purple {
    background: rgba(139, 92, 246, 0.12);
    color: #C084FC;
    border-color: rgba(192, 132, 252, 0.25);
}

.page-header {
    margin-bottom: 1.2rem;
}

.page-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 0.25rem;
}

.page-header p {
    font-size: 0.92rem;
    color: #94A3B8;
    margin-bottom: 0;
}

.kpi-card {
    background: #151D2F;
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.kpi-card:hover {
    border-color: rgba(96, 165, 250, 0.35);
}

.kpi-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.82rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: #F8FAFC;
    margin: 8px 0 4px 0;
}

.kpi-subtext {
    font-size: 0.78rem;
    color: #64748B;
}

.saas-card {
    background: #151D2F;
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
}

.saas-card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 12px;
}

.filter-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #151D2F;
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 1.5rem;
}

.agent-response-card {
    background: #151D2F;
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 14px;
    padding: 18px;
    margin-top: 12px;
    margin-bottom: 16px;
}

.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    background: rgba(139, 92, 246, 0.16);
    color: #C084FC;
    border: 1px solid rgba(192, 132, 252, 0.3);
    margin-bottom: 10px;
}

.starter-card {
    background: rgba(21, 29, 47, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 12px;
    padding: 14px;
    text-align: left;
    height: 100%;
}
.starter-card h4 {
    margin: 6px 0 2px 0;
    font-size: 0.95rem;
    color: #F8FAFC;
}
.starter-card p {
    margin: 0;
    font-size: 0.8rem;
    color: #94A3B8;
}

/* Streamlit Chart Container Overrides in Dark Mode */
div[data-testid="stVegaLiteChart"],
.stPlotlyChart,
.js-plotly-plot,
.vega-embed,
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    background-color: #151D2F !important;
    background: #151D2F !important;
    border: 1px solid rgba(148, 163, 184, 0.15) !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

div[data-testid="stVegaLiteChart"] svg,
div[data-testid="stVegaLiteChart"] canvas,
.vega-embed svg,
.vega-embed canvas {
    background-color: #151D2F !important;
    background: #151D2F !important;
}

.vega-embed .background {
    fill: #151D2F !important;
}
</style>
"""

SAAS_LIGHT_CSS = """
<style>
/* Global SaaS Workspace Theme - Light Mode */
.stApp {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

header[data-testid="stHeader"] {
    background-color: rgba(248, 250, 252, 0.85) !important;
    backdrop-filter: blur(8px);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Sidebar Navigation Buttons in Light Mode */
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] .stButton > button {
    background-color: #F1F5F9 !important;
    color: #1E293B !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] button:hover,
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #E2E8F0 !important;
    color: #0F172A !important;
    border-color: #CBD5E1 !important;
}

section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[type="primary"] {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    font-weight: 700 !important;
}

/* Main Content Text Inputs in Light Mode */
div[data-testid="stMain"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
.stTextInput > div > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

div[data-testid="stMain"] input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* Main Content Action Buttons in Light Mode */
div[data-testid="stMain"] button,
div[data-testid="stMain"] .stButton > button {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(59, 130, 246, 0.2) !important;
}

div[data-testid="stMain"] button:hover,
div[data-testid="stMain"] .stButton > button:hover {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border-color: #1D4ED8 !important;
}

/* Top SaaS Bar */
.saas-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px;
    padding: 10px 20px;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

.saas-topbar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F172A !important;
}

.saas-topbar-badges {
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid #CBD5E1 !important;
}

.status-pill-green {
    background: rgba(34, 197, 94, 0.1) !important;
    color: #15803D !important;
    border-color: rgba(34, 197, 94, 0.3) !important;
}

.status-pill-blue {
    background: rgba(59, 130, 246, 0.1) !important;
    color: #1D4ED8 !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
}

.status-pill-purple {
    background: rgba(139, 92, 246, 0.1) !important;
    color: #6D28D9 !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* Page Header */
.page-header {
    margin-bottom: 1.2rem;
}

.page-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0F172A !important;
    margin-bottom: 0.25rem;
}

.page-header p {
    font-size: 0.92rem;
    color: #64748B !important;
    margin-bottom: 0;
}

/* KPI Card */
.kpi-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.kpi-card:hover {
    border-color: #93C5FD !important;
    transform: translateY(-1px);
}

.kpi-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: #0F172A !important;
    margin: 8px 0 4px 0;
}

.kpi-subtext {
    font-size: 0.78rem;
    color: #64748B !important;
}

/* Card Container */
.saas-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
}

.saas-card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0F172A !important;
    margin-bottom: 12px;
}

/* Filter Bar Container */
.filter-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 1.5rem;
    color: #0F172A !important;
}

/* Streamlit Selectbox / Input Controls in Light Mode */
div[data-baseweb="select"] > div,
.stSelectbox > div > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #0F172A !important;
}

/* Streamlit Tabs in Light Mode */
button[data-baseweb="tab"] {
    color: #64748B !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #2563EB !important;
    border-bottom-color: #2563EB !important;
}

/* Expanders in Light Mode */
div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
}

div[data-testid="stExpander"] summary {
    color: #0F172A !important;
    font-weight: 600 !important;
}

/* Sliders in Light Mode */
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] p,
div[data-testid="stSlider"] div {
    color: #0F172A !important;
}

/* Streamlit Charts (Vega / Altair / Dataframe) Overrides in Light Mode */
div[data-testid="stVegaLiteChart"],
.stPlotlyChart,
.js-plotly-plot,
.vega-embed,
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
}

div[data-testid="stVegaLiteChart"] summary,
div[data-testid="stVegaLiteChart"] svg,
div[data-testid="stVegaLiteChart"] canvas,
.vega-embed svg,
.vega-embed canvas {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
}

.vega-embed .background {
    fill: #FFFFFF !important;
}

.vega-embed text {
    fill: #334155 !important;
}

.vega-embed .role-axis text,
.vega-embed .role-axis-title text {
    fill: #475569 !important;
}

.vega-embed .role-axis-grid line {
    stroke: #F1F5F9 !important;
}

.vega-embed .role-legend text {
    fill: #1E293B !important;
}

/* Agent Response Card */
.agent-response-card {
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px;
    padding: 18px;
    margin-top: 12px;
    margin-bottom: 16px;
}

.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    background: rgba(139, 92, 246, 0.12) !important;
    color: #6D28D9 !important;
    border: 1px solid rgba(139, 92, 246, 0.25) !important;
    margin-bottom: 10px;
}

/* Starter Card */
.starter-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px;
    padding: 14px;
    text-align: left;
    height: 100%;
}
.starter-card h4 {
    margin: 6px 0 2px 0;
    font-size: 0.95rem;
    color: #0F172A !important;
}
.starter-card p {
    margin: 0;
    font-size: 0.8rem;
    color: #64748B !important;
}
</style>
"""


def apply_saas_theme():
    """Inject custom enterprise CSS into Streamlit page based on active theme mode."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    if theme_mode == "light":
        st.markdown(SAAS_LIGHT_CSS, unsafe_allow_html=True)
    else:
        st.markdown(SAAS_DARK_CSS, unsafe_allow_html=True)
