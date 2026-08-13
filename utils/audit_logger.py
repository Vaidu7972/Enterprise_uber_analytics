import sys
from datetime import datetime
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

def ensure_audit_table_exists():
    """Ensure audit schema and etl_batch_log table exist."""
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS audit;"))
        conn.execute(
            text("""
                CREATE TABLE IF NOT EXISTS audit.etl_batch_log
                (
                    batch_id SERIAL PRIMARY KEY,
                    pipeline_name VARCHAR(100),
                    task_name VARCHAR(100),
                    source_name VARCHAR(150),
                    target_table VARCHAR(150),
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status VARCHAR(30),
                    rows_read INT DEFAULT 0,
                    rows_inserted INT DEFAULT 0,
                    rows_updated INT DEFAULT 0,
                    rows_rejected INT DEFAULT 0,
                    last_watermark TIMESTAMP,
                    error_message TEXT
                );
            """)
        )


def start_batch_log(pipeline_name: str, task_name: str, source_name: str, target_table: str) -> int:
    """
    Inserts a running status entry into audit.etl_batch_log.
    Returns the generated batch_id.
    """
    ensure_audit_table_exists()
    sql = text("""
        INSERT INTO audit.etl_batch_log
        (pipeline_name, task_name, source_name, target_table, start_time, status)
        VALUES
        (:pipeline_name, :task_name, :source_name, :target_table, CURRENT_TIMESTAMP, 'RUNNING')
        RETURNING batch_id;
    """)
    with engine.begin() as conn:
        result = conn.execute(
            sql,
            {
                "pipeline_name": pipeline_name,
                "task_name": task_name,
                "source_name": source_name,
                "target_table": target_table,
            },
        )
        batch_id = result.scalar()
        print(f"[AUDIT] Started batch_id={batch_id} for task='{task_name}', target='{target_table}'")
        return batch_id


def update_batch_success(
    batch_id: int,
    rows_read: int = 0,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    rows_rejected: int = 0,
    last_watermark=None,
):
    """Updates batch status to SUCCESS with metrics and watermark."""
    ensure_audit_table_exists()
    sql = text("""
        UPDATE audit.etl_batch_log
        SET
            end_time = CURRENT_TIMESTAMP,
            status = 'SUCCESS',
            rows_read = :rows_read,
            rows_inserted = :rows_inserted,
            rows_updated = :rows_updated,
            rows_rejected = :rows_rejected,
            last_watermark = :last_watermark
        WHERE batch_id = :batch_id;
    """)
    with engine.begin() as conn:
        conn.execute(
            sql,
            {
                "batch_id": batch_id,
                "rows_read": rows_read,
                "rows_inserted": rows_inserted,
                "rows_updated": rows_updated,
                "rows_rejected": rows_rejected,
                "last_watermark": last_watermark,
            },
        )
        print(
            f"[AUDIT] Completed batch_id={batch_id} STATUS=SUCCESS "
            f"(Read: {rows_read}, Ins: {rows_inserted}, Upd: {rows_updated}, Rej: {rows_rejected}, Watermark: {last_watermark})"
        )


def update_batch_failure(batch_id: int, error_message: str):
    """Updates batch status to FAILED with error details."""
    ensure_audit_table_exists()
    sql = text("""
        UPDATE audit.etl_batch_log
        SET
            end_time = CURRENT_TIMESTAMP,
            status = 'FAILED',
            error_message = :error_message
        WHERE batch_id = :batch_id;
    """)
    with engine.begin() as conn:
        conn.execute(
            sql,
            {
                "batch_id": batch_id,
                "error_message": str(error_message),
            },
        )
        print(f"[AUDIT] Failed batch_id={batch_id} STATUS=FAILED - Error: {error_message}")
