import os
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine

@st.cache_data(ttl=15)
def check_postgres_connection() -> bool:
    """Verify PostgreSQL database connectivity."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

@st.cache_data(ttl=15)
def check_gold_schema() -> bool:
    """Verify Gold schema exists and contains data."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            res = conn.execute(text("SELECT COUNT(*) FROM gold.kpi_summary")).scalar()
            return res is not None and res > 0
    except Exception:
        return False

@st.cache_data(ttl=60)
def check_gemini_configuration() -> bool:
    """Verify Gemini API key configuration."""
    return bool(os.getenv("GEMINI_API_KEY"))

@st.cache_data(ttl=60)
def check_ml_model() -> bool:
    """Verify RandomForest driver risk ML model availability."""
    try:
        from agentic_ai.tools.ml_tool import predict_driver_risk
        res = predict_driver_risk()
        return bool(res.get("found"))
    except Exception:
        return False

@st.cache_data(ttl=60)
def check_vector_store() -> bool:
    """Verify ChromaDB vector store collection readiness."""
    try:
        from agentic_ai.rag.vector_store import collection
        return collection.count() >= 0
    except Exception:
        return False

@st.cache_data(ttl=15)
def check_pipeline_health() -> dict:
    """Check latest Airflow ETL execution status and watermark."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT status, end_time, last_watermark FROM audit.etl_batch_log ORDER BY batch_id DESC LIMIT 1")
            ).mappings().first()
            if row:
                return {
                    "connected": True,
                    "status": row["status"] or "UNKNOWN",
                    "last_refresh": row["end_time"].strftime("%H:%M") if row["end_time"] else "N/A",
                    "watermark": str(row["last_watermark"]) if row["last_watermark"] else "N/A"
                }
    except Exception:
        pass
    return {"connected": False, "status": "OFFLINE", "last_refresh": "N/A", "watermark": "N/A"}
