import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg

SAAS_CSS = """
<style>
/* Global SaaS Workspace Theme */
.stApp {
    background-color: #0B101D;
    color: #F8FAFC;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Hide default Streamlit decoration */
header[data-testid="stHeader"] {
    background-color: rgba(11, 16, 29, 0.85);
    backdrop-filter: blur(8px);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid rgba(148, 163, 184, 0.12) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Top SaaS Bar */
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

/* Page Header */
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

/* KPI Card */
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

/* Card Container */
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

/* Filter Bar Container */
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

/* Agent Response Card */
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

/* Starter Card */
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
</style>
"""


def apply_saas_theme():
    """Inject custom enterprise CSS into Streamlit page."""
    st.markdown(SAAS_CSS, unsafe_allow_html=True)
