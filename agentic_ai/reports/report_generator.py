import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from agentic_ai.config.agent_config import REPORTS_DIR

def generate_pdf_report(investigation_data: dict, filename: str = None) -> str:
    """
    Generate a professional PDF report for UberOps AI investigations.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"UberOps_Investigation_{timestamp}.pdf"

    pdf_path = REPORTS_DIR / filename
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1E1B4B'), spaceAfter=12)
    heading_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor('#4338CA'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor('#334155'))

    story = []

    # Title
    story.append(Paragraph("🚕 UberOps AI — Executive Investigation Report", title_style))
    story.append(Paragraph(f"<b>Generated Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <b>Platform:</b> UberOps Data Intelligence", body_style))
    story.append(Spacer(1, 12))

    # User Question
    q = investigation_data.get("question", "N/A")
    story.append(Paragraph("1. Primary Question / Target Scope", heading_style))
    story.append(Paragraph(f"<i>{q}</i>", body_style))
    story.append(Spacer(1, 10))

    # Executive Summary / Final Answer
    answer = investigation_data.get("answer", "No response text available.")
    # Replace markdown headers with HTML bold for ReportLab
    clean_answer = answer.replace("### ", "<b>").replace("#### ", "<b>").replace("---", "").replace("* ", "• ")
    story.append(Paragraph("2. Executive Investigation Findings", heading_style))
    story.append(Paragraph(clean_answer.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))

    # Insights & Recommendations
    recs = investigation_data.get("recommendations", {})
    if recs:
        story.append(Paragraph("3. Recommended Operational Actions", heading_style))
        story.append(Paragraph(f"<b>Primary Recommendation:</b> {recs.get('primary_recommendation', 'N/A')}", body_style))
        story.append(Paragraph(f"<b>Manager Approval Required:</b> {'YES' if recs.get('approval_required') else 'NO'}", body_style))
        story.append(Spacer(1, 10))

    # Sources & Attribution
    sources = investigation_data.get("sources", [])
    if sources:
        story.append(Paragraph("4. Support Policy Sources Grounding", heading_style))
        sources_str = ", ".join([f"{s['source']} (Page {s['page']})" for s in sources])
        story.append(Paragraph(f"Evidence retrieved from: {sources_str}", body_style))

    doc.build(story)
    return str(pdf_path)
