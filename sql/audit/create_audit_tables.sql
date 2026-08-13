-- ===========================================
-- Audit Schema
-- ===========================================

CREATE SCHEMA IF NOT EXISTS audit;

-- ETL Batch Log Table
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
