import pandas as pd
import streamlit as st
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card


def render_predictions_page():
    """Render SaaS Predictive Intelligence Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Predictive Intelligence</h1>
            <p>RandomForest machine learning risk scoring on Gold warehouse driver features.</p>
        </div>
    """, unsafe_allow_html=True)

    batch_ml = predict_driver_risk()
    if batch_ml.get("found"):
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Scored Drivers", f"{batch_ml.get('total_drivers_scored')}", "Users", "Total Fleet Drivers", "#3B82F6", change_text="Active ML Model", is_positive=True)
        with m2:
            render_kpi_card("High Risk", f"{batch_ml.get('high_risk_count')}", "TriangleAlert", "Requires Action", "#EF4444", change_text="49.2%", is_positive=False)
        with m3:
            render_kpi_card("Medium Risk", f"{batch_ml.get('medium_risk_count')}", "Clock", "Monitor Performance", "#F59E0B", change_text="0.0%", is_positive=True)
        with m4:
            render_kpi_card("Low Risk", f"{batch_ml.get('low_risk_count')}", "CircleCheck", "Optimal Performance", "#10B981", change_text="50.8%", is_positive=True)

        st.divider()

        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} High-Risk Driver Leaderboard</div>""", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(batch_ml.get("top_high_risk_drivers", [])), use_container_width=True, hide_index=True)

        meta = batch_ml.get("model_info", {})
        if meta.get("importances"):
            st.divider()
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('BrainCircuit', '#8B5CF6', 18)} Feature Importances</div>""", unsafe_allow_html=True)
            st.bar_chart(pd.Series(meta["importances"]))
