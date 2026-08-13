import streamlit as st
from agentic_ai.agents.report_agent import generate_executive_report
from agentic_ai.ui.styles.icons import get_icon_svg


def render_reports_page():
    """Render SaaS Reports Center Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Reports Center</h1>
            <p>Generate, preview, and download formal executive performance reports in PDF, HTML, and CSV formats.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('FileText', '#3B82F6', 18)} Executive Report Generator</div>""", unsafe_allow_html=True)
    
    rep_type = st.selectbox("Select Report Type", [
        "Executive Performance Report",
        "Revenue Analysis Report",
        "Driver Performance Report",
        "AI Investigation Report",
        "Data Quality Report",
    ])

    if st.button("Generate & Compile Report"):
        with st.spinner("Report Agent compiling warehouse analytics into PDF/HTML/CSV..."):
            rep_res = generate_executive_report(report_type=rep_type)
            st.success("Report generated successfully!")

            r1, r2, r3 = st.columns(3)
            with r1:
                with open(rep_res["pdf_path"], "rb") as f:
                    st.download_button("Download PDF Report", f.read(), file_name=f"{rep_type.replace(' ', '_')}.pdf", mime="application/pdf")
            with r2:
                with open(rep_res["html_path"], "rb") as f:
                    st.download_button("Download HTML Report", f.read(), file_name=f"{rep_type.replace(' ', '_')}.html", mime="text/html")
            with r3:
                with open(rep_res["csv_path"], "rb") as f:
                    st.download_button("Download CSV Data", f.read(), file_name=f"{rep_type.replace(' ', '_')}.csv", mime="text/csv")
