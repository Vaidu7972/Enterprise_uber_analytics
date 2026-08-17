import os
import datetime
import streamlit as st
from agentic_ai.agents.report_agent import generate_executive_report
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card

SUPPORTED_REPORTS = [
    {
        "type": "Executive Performance Report",
        "icon": "FileText",
        "color": "#3B82F6",
        "description": "Comprehensive operational summary of revenue, trips, driver performance, and ETL watermark status.",
        "formats": ["PDF", "HTML", "CSV"],
    },
    {
        "type": "Revenue Analysis Report",
        "icon": "TrendingUp",
        "color": "#10B981",
        "description": "In-depth breakdown of weekday vs weekend revenue, average fare yields, and daily variance trends.",
        "formats": ["PDF", "HTML", "CSV"],
    },
    {
        "type": "Driver Performance Report",
        "icon": "Users",
        "color": "#F59E0B",
        "description": "Individual driver revenue leaderboard, rating distributions, and ML underperformance risk flags.",
        "formats": ["PDF", "HTML", "CSV"],
    },
    {
        "type": "AI Investigation Report",
        "icon": "BrainCircuit",
        "color": "#8B5CF6",
        "description": "Multi-agent intent classification audit, generated Gold SQL queries, and evidence reflection logs.",
        "formats": ["PDF", "HTML", "CSV"],
    },
    {
        "type": "Data Quality Report",
        "icon": "ShieldCheck",
        "color": "#06B6D4",
        "description": "Silver schema validation audit, clean pass rate metrics, and rejected record categorization.",
        "formats": ["PDF", "HTML", "CSV"],
    },
]

def render_reports_page():
    """Render SaaS Reports Center Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Reports Center</h1>
            <p>Generate, preview, and export formal executive mobility reports in PDF, HTML, and CSV formats.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Available Reports", f"{len(SUPPORTED_REPORTS)}", "FileText", "Executive Templates", "#3B82F6")
    with c2:
        render_kpi_card("Export Formats", "PDF / HTML / CSV", "Workflow", "Multi-Format Output", "#10B981")
    with c3:
        render_kpi_card("Report Engine", "ReportLab PDF", "Bot", "Automated Generation", "#8B5CF6")

    st.divider()

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('FileText', '#3B82F6', 18)} Executive Report Generator</div>""", unsafe_allow_html=True)

    selected_report_type = st.selectbox(
        "Select Report Template",
        [r["type"] for r in SUPPORTED_REPORTS],
        key="rep_template_sel"
    )

    # Find description
    rep_info = next((r for r in SUPPORTED_REPORTS if r["type"] == selected_report_type), SUPPORTED_REPORTS[0])
    st.info(f"**Report Description:** {rep_info['description']}")

    if st.button("Generate & Compile Report Package", key="btn_generate_rep", type="primary"):
        with st.spinner("Report Agent compiling warehouse analytics into PDF, HTML, and CSV packages..."):
            try:
                rep_res = generate_executive_report(report_type=selected_report_type)
                st.success(f"'{selected_report_type}' generated successfully!")

                r1, r2, r3 = st.columns(3)
                with r1:
                    if os.path.exists(rep_res["pdf_path"]):
                        with open(rep_res["pdf_path"], "rb") as f:
                            st.download_button("Download PDF Report", f.read(), file_name=f"{selected_report_type.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
                with r2:
                    if os.path.exists(rep_res["html_path"]):
                        with open(rep_res["html_path"], "rb") as f:
                            st.download_button("Download HTML Report", f.read(), file_name=f"{selected_report_type.replace(' ', '_')}.html", mime="text/html", use_container_width=True)
                with r3:
                    if os.path.exists(rep_res["csv_path"]):
                        with open(rep_res["csv_path"], "rb") as f:
                            st.download_button("Download CSV Data", f.read(), file_name=f"{selected_report_type.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
            except Exception as ex:
                st.error(f"Report Generation Error: {ex}")
