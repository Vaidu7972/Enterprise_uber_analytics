import json
from datetime import datetime
from sqlalchemy import text
from utils.db_connection import get_engine

def init_audit_tables():
    """
    Initialize audit and investigation history tables in PostgreSQL Gold schema.
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
                approved_by VARCHAR(100)
            );

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
