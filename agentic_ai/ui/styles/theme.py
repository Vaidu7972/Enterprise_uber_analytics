import streamlit as st

SAAS_DARK_CSS = """
<style>
/* Global Enterprise SaaS Theme - Dark Mode */
.stApp {
    background-color: #080D18 !important;
    color: #F8FAFC !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

header[data-testid="stHeader"] {
    background-color: rgba(8, 13, 24, 0.85) !important;
    backdrop-filter: blur(10px);
}

section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid rgba(148, 163, 184, 0.14) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* Sidebar Buttons */
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(17, 24, 39, 0.7) !important;
    color: #E2E8F0 !important;
    border: 1px solid rgba(148, 163, 184, 0.14) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease-in-out !important;
}

section[data-testid="stSidebar"] button:hover,
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(30, 41, 59, 0.9) !important;
    color: #F8FAFC !important;
    border-color: rgba(59, 130, 246, 0.4) !important;
}

section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[type="primary"] {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #3B82F6 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}

/* Main Buttons */
div[data-testid="stMain"] button,
div[data-testid="stMain"] .stButton > button {
    background-color: #151D2F !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease-in-out !important;
}

div[data-testid="stMain"] button:hover,
div[data-testid="stMain"] .stButton > button:hover {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border-color: rgba(59, 130, 246, 0.4) !important;
}

div[data-testid="stMain"] button[kind="primary"],
div[data-testid="stMain"] button[type="primary"],
div[data-testid="stMain"] button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
}

/* Semantic Action Buttons (Approve / Reject) */
.stButton > button[data-testid="btn-approve"],
button.approve-btn {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #059669 !important;
}

.stButton > button[data-testid="btn-reject"],
button.reject-btn {
    background: rgba(239, 68, 68, 0.15) !important;
    color: #EF4444 !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
}

/* Form Controls and Inputs */
div[data-testid="stMain"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 8px !important;
}

/* Top SaaS Bar Header */
.saas-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 12px;
    padding: 10px 20px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.saas-topbar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.15rem;
    font-weight: 800;
    color: #F8FAFC;
}

.saas-topbar-badges {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Status Pills */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

.status-pill-green {
    background: rgba(16, 185, 129, 0.12);
    color: #10B981;
    border-color: rgba(16, 185, 129, 0.3);
}

.status-pill-blue {
    background: rgba(59, 130, 246, 0.12);
    color: #3B82F6;
    border-color: rgba(59, 130, 246, 0.3);
}

.status-pill-purple {
    background: rgba(139, 92, 246, 0.12);
    color: #8B5CF6;
    border-color: rgba(139, 92, 246, 0.3);
}

.status-pill-amber {
    background: rgba(245, 158, 11, 0.12);
    color: #F59E0B;
    border-color: rgba(245, 158, 11, 0.3);
}

.status-pill-red {
    background: rgba(239, 68, 68, 0.12);
    color: #EF4444;
    border-color: rgba(239, 68, 68, 0.3);
}

/* Page Header */
.page-header {
    margin-bottom: 1.2rem;
}

.page-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 0.25rem;
    letter-spacing: -0.5px;
}

.page-header p {
    font-size: 0.92rem;
    color: #94A3B8;
    margin-bottom: 0;
}

/* Cards */
.kpi-card {
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.kpi-card:hover {
    border-color: rgba(59, 130, 246, 0.35);
    transform: translateY(-2px);
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
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
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
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 1.5rem;
}

.agent-response-card {
    background: #111827;
    border: 1px solid rgba(139, 92, 246, 0.3);
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
    border: 1px solid rgba(139, 92, 246, 0.3);
    margin-bottom: 10px;
}

/* Streamlit Chart Containers in Dark Mode */
div[data-testid="stVegaLiteChart"],
.stPlotlyChart,
.js-plotly-plot,
.vega-embed,
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    background-color: #111827 !important;
    background: #111827 !important;
    border: 1px solid rgba(148, 163, 184, 0.14) !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

div[data-testid="stVegaLiteChart"] svg,
div[data-testid="stVegaLiteChart"] canvas,
.vega-embed svg,
.vega-embed canvas {
    background-color: #111827 !important;
    background: #111827 !important;
}

.vega-embed .background {
    fill: #111827 !important;
}
</style>
"""

SAAS_LIGHT_CSS = """
<style>
/* Global Enterprise SaaS Theme - Light Mode */
.stApp {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

header[data-testid="stHeader"] {
    background-color: rgba(248, 250, 252, 0.85) !important;
    backdrop-filter: blur(10px);
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* Sidebar Buttons in Light Mode */
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
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    font-weight: 700 !important;
}

/* Main Content Text Inputs in Light Mode */
div[data-testid="stMain"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

/* Main Buttons in Light Mode */
div[data-testid="stMain"] button,
div[data-testid="stMain"] .stButton > button {
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

div[data-testid="stMain"] button:hover,
div[data-testid="stMain"] .stButton > button:hover {
    background-color: #E2E8F0 !important;
    color: #0F172A !important;
    border-color: #94A3B8 !important;
}

div[data-testid="stMain"] button[kind="primary"],
div[data-testid="stMain"] button[type="primary"],
div[data-testid="stMain"] button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    font-weight: 700 !important;
}

/* Top SaaS Bar in Light Mode */
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
    font-weight: 800;
    color: #0F172A !important;
}

.saas-topbar-badges {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    border: 1px solid #CBD5E1 !important;
}

.status-pill-green {
    background: rgba(16, 185, 129, 0.1) !important;
    color: #059669 !important;
    border-color: rgba(16, 185, 129, 0.3) !important;
}

.status-pill-blue {
    background: rgba(59, 130, 246, 0.1) !important;
    color: #2563EB !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
}

.status-pill-purple {
    background: rgba(139, 92, 246, 0.1) !important;
    color: #7C3AED !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

.status-pill-amber {
    background: rgba(245, 158, 11, 0.1) !important;
    color: #D97706 !important;
    border-color: rgba(245, 158, 11, 0.3) !important;
}

.status-pill-red {
    background: rgba(239, 68, 68, 0.1) !important;
    color: #DC2626 !important;
    border-color: rgba(239, 68, 68, 0.3) !important;
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

.kpi-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
}

.kpi-card:hover {
    border-color: #93C5FD !important;
    transform: translateY(-2px);
}

.kpi-header {
    color: #64748B !important;
}

.kpi-value {
    color: #0F172A !important;
}

.kpi-subtext {
    color: #64748B !important;
}

.saas-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
}

.saas-card-title {
    color: #0F172A !important;
}

.filter-bar {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    color: #0F172A !important;
}

/* Streamlit Chart Containers in Light Mode */
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
}

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

/* Selectbox & Dropdowns in Light Mode */
div[data-baseweb="select"] > div,
.stSelectbox > div > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
}

div[role="listbox"],
ul[role="listbox"],
li[role="option"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

/* General Typography in Light Mode */
div[data-testid="stMain"] p,
div[data-testid="stMain"] span,
div[data-testid="stMain"] label,
div[data-testid="stMain"] h1,
div[data-testid="stMain"] h2,
div[data-testid="stMain"] h3,
div[data-testid="stMain"] h4,
div[data-testid="stMain"] h5,
div[data-testid="stMain"] h6 {
    color: #0F172A;
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
