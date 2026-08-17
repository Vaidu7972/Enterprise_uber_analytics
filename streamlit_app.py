import streamlit as st

from agentic_ai.ui.styles.theme import apply_saas_theme
from agentic_ai.ui.components.header import render_saas_header
from agentic_ai.ui.components.sidebar import render_saas_sidebar

from agentic_ai.ui.pages.overview import render_overview_page
from agentic_ai.ui.pages.assistant import render_assistant_page
from agentic_ai.ui.pages.revenue import render_revenue_page
from agentic_ai.ui.pages.drivers import render_drivers_page
from agentic_ai.ui.pages.operations import render_operations_page
from agentic_ai.ui.pages.knowledge import render_knowledge_page
from agentic_ai.ui.pages.predictions import render_predictions_page
from agentic_ai.ui.pages.prediction_studio import render_prediction_studio_page
from agentic_ai.ui.pages.action_center import render_action_center_page
from agentic_ai.ui.pages.pipeline import render_pipeline_page
from agentic_ai.ui.pages.quality import render_quality_page
from agentic_ai.ui.pages.warehouse import render_warehouse_page
from agentic_ai.ui.pages.reports import render_reports_page
from agentic_ai.ui.pages.activity import render_activity_page
from agentic_ai.ui.pages.audit import render_audit_page
from agentic_ai.ui.pages.settings import render_settings_page

# Page Configuration
st.set_page_config(
    page_title="UberOps AI — Enterprise Mobility Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Enterprise SaaS CSS Theme
apply_saas_theme()

# Render Top Bar Header
render_saas_header()

# Render SaaS Sidebar Navigation & Route Page
selected_page = render_saas_sidebar()

if selected_page == "Overview":
    render_overview_page()
elif selected_page == "AI Assistant":
    render_assistant_page()
elif selected_page == "Revenue Intelligence":
    render_revenue_page()
elif selected_page == "Driver Intelligence":
    render_drivers_page()
elif selected_page == "Operations Analytics":
    render_operations_page()
elif selected_page == "Knowledge Center":
    render_knowledge_page()
elif selected_page == "Predictive Intelligence":
    render_predictions_page()
elif selected_page == "Prediction Studio":
    render_prediction_studio_page()
elif selected_page == "Action Center":
    render_action_center_page()
elif selected_page == "Pipeline Health":
    render_pipeline_page()
elif selected_page == "Data Quality":
    render_quality_page()
elif selected_page == "Warehouse Explorer":
    render_warehouse_page()
elif selected_page == "Reports":
    render_reports_page()
elif selected_page == "Agent Activity":
    render_activity_page()
elif selected_page == "Audit Logs":
    render_audit_page()
elif selected_page == "Settings":
    render_settings_page()
else:
    render_overview_page()