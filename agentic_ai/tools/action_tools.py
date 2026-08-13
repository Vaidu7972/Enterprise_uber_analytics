import json
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.memory.persistent_memory import init_audit_tables


def create_training_recommendation(driver_id: str, driver_name: str, course_name: str = "Driver Quality & Hospitality Coaching", approved_by: str = "Manager") -> dict:
    """
    Action Tool: Assign mandatory training coaching to an underperforming driver upon manager approval.
    Does NOT mutate core trip/revenue warehouse data.
    """
    init_audit_tables()
    engine = get_engine()
    details = f"Assigned training module '{course_name}' to driver {driver_name} ({driver_id}). Duration: 7 days."
    
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO gold.action_logs (action_type, target_entity, details, status, approved_by)
            VALUES ('ASSIGN_TRAINING', :target_entity, :details, 'ACTIVE', :approved_by);
        """), {
            "target_entity": driver_id,
            "details": details,
            "approved_by": approved_by
        })
        conn.commit()

    return {
        "success": True,
        "action_type": "ASSIGN_TRAINING",
        "driver_id": driver_id,
        "details": details,
        "status": "ASSIGNED",
        "approved_by": approved_by
    }


def create_support_ticket(ticket_title: str, category: str, description: str, priority: str = "HIGH", approved_by: str = "Manager") -> dict:
    """
    Action Tool: Open a support ticket in the operations portal.
    """
    init_audit_tables()
    engine = get_engine()
    details = f"Support Ticket: {ticket_title} | Category: {category} | Priority: {priority} | Description: {description}"

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO gold.action_logs (action_type, target_entity, details, status, approved_by)
            VALUES ('CREATE_SUPPORT_TICKET', :target_entity, :details, 'OPEN', :approved_by);
        """), {
            "target_entity": category,
            "details": details,
            "approved_by": approved_by
        })
        conn.commit()

    return {
        "success": True,
        "action_type": "CREATE_SUPPORT_TICKET",
        "ticket_title": ticket_title,
        "priority": priority,
        "status": "OPEN",
        "approved_by": approved_by
    }


def save_investigation(question: str, data_summary: str, ml_summary: str, support_summary: str, recommended_action: str, approval_status: str = "APPROVED") -> dict:
    """
    Action Tool: Persist a multi-agent investigation report.
    """
    init_audit_tables()
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO gold.investigation_logs (question, data_summary, ml_summary, support_summary, recommended_action, approval_status)
            VALUES (:question, :data_summary, :ml_summary, :support_summary, :recommended_action, :approval_status);
        """), {
            "question": question,
            "data_summary": data_summary,
            "ml_summary": ml_summary,
            "support_summary": support_summary,
            "recommended_action": recommended_action,
            "approval_status": approval_status
        })
        conn.commit()

    return {
        "success": True,
        "message": "Investigation successfully saved to database."
    }
