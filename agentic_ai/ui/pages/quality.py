import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card
from agentic_ai.ui.components.charts import render_donut_chart, render_bar_chart

def render_quality_page():
    """Render SaaS Data Quality Scorecard Page based on actual Silver schema validation results."""
    st.markdown("""
        <div class="page-header">
            <h1>Data Quality Scorecard</h1>
            <p>Silver schema validation metrics, clean record throughput, and rejected record audit tracking.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            df_rej = pd.read_sql_query(text("SELECT COUNT(*) AS count FROM silver.trip_rejected;"), conn)
            df_clean = pd.read_sql_query(text("SELECT COUNT(*) AS count FROM silver.trip_clean;"), conn)

        rej_val = int(df_rej.iloc[0]["count"]) if not df_rej.empty else 0
        clean_val = int(df_clean.iloc[0]["count"]) if not df_clean.empty else 0
        total_checked = clean_val + rej_val

        pass_rate = (clean_val / total_checked * 100) if total_checked > 0 else 100.0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Rows Checked", f"{total_checked:,}", "ShieldCheck", "Total Validation Target", "#3B82F6", change_text="Validated", is_positive=True)
        with c2:
            render_kpi_card("Clean Records", f"{clean_val:,}", "CircleCheck", "Silver Clean Table", "#10B981", change_text="Clean Pass", is_positive=True)
        with c3:
            render_kpi_card("Rejected Records", f"{rej_val:,}", "TriangleAlert", "Silver Rejected Log", "#EF4444", change_text="Rejections", is_positive=False)
        with c4:
            render_kpi_card("Quality Pass Rate", f"{pass_rate:.2f}%", "Activity", "Calculated Pass Rate", "#8B5CF6", change_text="Pass Rate", is_positive=(pass_rate >= 95.0))

        st.divider()

        # Charts: Clean vs Rejected Donut & Rejection Reasons Breakdown
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('PieChart', '#3B82F6', 18)} Clean vs Rejected Record Breakdown</div>""", unsafe_allow_html=True)
            q_df = pd.DataFrame([
                {"Status": "Clean Records", "Count": clean_val},
                {"Status": "Rejected Records", "Count": rej_val},
            ])
            render_donut_chart(q_df, "Status", "Count", height=240)

        with r1_col2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('TriangleAlert', '#EF4444', 18)} Top Validation Rejection Categories</div>""", unsafe_allow_html=True)
            with engine.connect() as conn:
                df_rej_reasons = pd.read_sql_query(text("SELECT rejection_reason, COUNT(*) AS failure_count FROM silver.trip_rejected GROUP BY rejection_reason ORDER BY failure_count DESC LIMIT 5;"), conn)
            
            if not df_rej_reasons.empty:
                render_bar_chart(df_rej_reasons, "rejection_reason", "failure_count", color="#EF4444", title="Rejection Count", height=240)

        st.divider()

        if rej_val > 0:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Database', '#EF4444', 18)} Silver Rejected Records Inspection Log</div>""", unsafe_allow_html=True)
            with engine.connect() as conn:
                df_rej_log = pd.read_sql_query(text("SELECT * FROM silver.trip_rejected LIMIT 50;"), conn)
            st.dataframe(df_rej_log, use_container_width=True, hide_index=True)
            st.download_button("Download Rejected Records CSV", df_rej_log.to_csv(index=False), "rejected_records.csv", "text/csv")
    except Exception as ex:
        st.error(f"Could not load Data Quality scorecard: {ex}")
