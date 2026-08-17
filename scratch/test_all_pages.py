import streamlit as st

st.session_state.theme_mode = "dark"
st.session_state.current_page = "Overview"

from agentic_ai.ui.styles.theme import apply_saas_theme
from agentic_ai.ui.components.header import render_saas_header
from agentic_ai.ui.components.sidebar import render_saas_sidebar

print("Theme, header, sidebar imported successfully.")

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

print("All 16 page modules (including Prediction Studio) imported successfully without errors!")
