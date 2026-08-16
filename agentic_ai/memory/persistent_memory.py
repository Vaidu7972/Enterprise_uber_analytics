import json
from datetime import datetime
from sqlalchemy import text
from utils.db_connection import get_engine

def init_audit_tables():
    """
    Initialize audit, action, and investigation history tables in PostgreSQL Gold schema.
    """
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS gold.agent_audit_logs (
                log_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id VARCHAR(100),
                question TEXT,
                route VARCHAR(50),
                agent VARCHAR(50),
                tool_used VARCHAR(100),
                status VARCHAR(50),
                action_recommended TEXT,
                approval_status VARCHAR(50)
            );

            CREATE TABLE IF NOT EXISTS gold.action_logs (
                action_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type VARCHAR(100),
                target_entity VARCHAR(100),
                details TEXT,
                status VARCHAR(50),
                approved_by VARCHAR(100),
                rejection_reason TEXT,
                executed_at TIMESTAMP
            );

            ALTER TABLE gold.action_logs ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
            ALTER TABLE gold.action_logs ADD COLUMN IF NOT EXISTS executed_at TIMESTAMP;

            CREATE TABLE IF NOT EXISTS gold.investigation_logs (
                investigation_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                question TEXT,
                data_summary TEXT,
                ml_summary TEXT,
                support_summary TEXT,
                recommended_action TEXT,
                approval_status VARCHAR(50)
            );
        """))
        conn.commit()


def create_pending_action(action_type: str, target_entity: str, details: str) -> int:
    """
    Register a sensitive agent recommendation as PENDING manager approval.
    Does NOT execute the underlying tool.
    """
    init_audit_tables()
    engine = get_engine()
    with engine.connect() as conn:
        res = conn.execute(text("""
            INSERT INTO gold.action_logs (action_type, target_entity, details, status)
            VALUES (:action_type, :target_entity, :details, 'PENDING')
            RETURNING action_id;
        """), {
            "action_type": action_type,
            "target_entity": target_entity,
            "details": details
        })
        action_id = res.scalar()
        conn.commit()
        return action_id


def get_pending_actions() -> list[dict]:
    """
    Fetch all operational actions currently awaiting Human-in-the-Loop manager approval.
    """
    try:
        init_audit_tables()
        engine = get_engine()
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT action_id, timestamp, action_type, target_entity, details, status
                FROM gold.action_logs
                WHERE status = 'PENDING'
                ORDER BY timestamp DESC;
            """)).mappings().all()
            return [dict(r) for r in res]
    except Exception:
        return []


def get_all_action_logs(limit: int = 50) -> list[dict]:
    """
    Fetch complete audit trail of actions (PENDING, APPROVED, REJECTED).
    """
    try:
        init_audit_tables()
        engine = get_engine()
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT action_id, timestamp, action_type, target_entity, details, status, approved_by, rejection_reason, executed_at
                FROM gold.action_logs
                ORDER BY timestamp DESC
                LIMIT :limit;
            """), {"limit": limit}).mappings().all()
            return [dict(r) for r in res]
    except Exception:
        return []


def approve_pending_action(action_id: int, approved_by: str = "Manager") -> dict:
    """
    Approve pending action in PostgreSQL and mark it as APPROVED.
    """
    init_audit_tables()
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE gold.action_logs
            SET status = 'APPROVED', approved_by = :approved_by, executed_at = CURRENT_TIMESTAMP
            WHERE action_id = :action_id;
        """), {
            "action_id": action_id,
            "approved_by": approved_by
        })
        conn.commit()
    log_agent_activity("Manager approved action", "action_center", "Human Manager", status="success", approval_status="APPROVED")
    return {"success": True, "action_id": action_id, "status": "APPROVED", "approved_by": approved_by}


def reject_pending_action(action_id: int, rejection_reason: str = "Manager rejected", rejected_by: str = "Manager") -> dict:
    """
    Reject pending action in PostgreSQL and log rejection reason without executing action tool.
    """
    init_audit_tables()
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE gold.action_logs
            SET status = 'REJECTED', approved_by = :rejected_by, rejection_reason = :rejection_reason, executed_at = CURRENT_TIMESTAMP
            WHERE action_id = :action_id;
        """), {
            "action_id": action_id,
            "rejected_by": rejected_by,
            "rejection_reason": rejection_reason
        })
        conn.commit()
    log_agent_activity("Manager rejected action", "action_center", "Human Manager", status="rejected", approval_status="REJECTED")
    return {"success": True, "action_id": action_id, "status": "REJECTED", "rejection_reason": rejection_reason}


def log_agent_activity(question: str, route: str, agent: str, tool_used: str = None, status: str = "success", action_recommended: str = None, approval_status: str = "N/A", session_id: str = "session_default"):
    """
    Persist structured agent activity log into PostgreSQL.
    """
    try:
        init_audit_tables()
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO gold.agent_audit_logs (session_id, question, route, agent, tool_used, status, action_recommended, approval_status)
                VALUES (:session_id, :question, :route, :agent, :tool_used, :status, :action_recommended, :approval_status);
            """), {
                "session_id": session_id,
                "question": question,
                "route": route,
                "agent": agent,
                "tool_used": tool_used,
                "status": status,
                "action_recommended": action_recommended,
                "approval_status": approval_status
            })
            conn.commit()
    except Exception as e:
        print(f"Warning: Failed to persist agent audit log: {e}")


def get_recent_audit_logs(limit: int = 50) -> list[dict]:
    """
    Retrieve recent audit logs from PostgreSQL.
    """
    try:
        init_audit_tables()
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT log_id, timestamp, question, route, agent, status, action_recommended, approval_status
                FROM gold.agent_audit_logs
                ORDER BY timestamp DESC
                LIMIT :limit;
            """), {"limit": limit}).mappings().all()
            return [dict(r) for r in result]
    except Exception:
        return []
