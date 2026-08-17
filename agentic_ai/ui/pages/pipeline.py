import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.db_connection import get_engine
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import render_bar_chart, render_donut_chart

def render_pipeline_page():
    """Render SaaS Pipeline Health Page with Airflow ETL telemetry."""
    st.markdown("""
        <div class="page-header">
            <h1>Pipeline Health</h1>
            <p>Airflow DAG execution status, batch timing, incremental watermark tracking, and ingestion audit log from audit.etl_batch_log.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            df_etl = pd.read_sql_query(
                text("SELECT batch_id, pipeline_name, task_name, target_table, status, rows_read, rows_inserted, rows_updated, rows_rejected, last_watermark, start_time, end_time, error_message FROM audit.etl_batch_log ORDER BY batch_id DESC LIMIT 50;"),
                conn
            )

        if not df_etl.empty:
            latest_status = df_etl.iloc[0]["status"]
            latest_watermark = str(df_etl.iloc[0]["last_watermark"])
            total_batches = len(df_etl)
            succ_count = len(df_etl[df_etl["status"] == "SUCCESS"])
            fail_count = len(df_etl[df_etl["status"] == "FAILED"])
            tot_rows = int(df_etl["rows_inserted"].sum())

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                render_kpi_card("Last Batch Status", latest_status, "Workflow", "Airflow Execution", "#3B82F6", change_text="Live Telemetry", is_positive=(latest_status == "SUCCESS"))
            with c2:
                render_kpi_card("Successful Tasks", f"{succ_count}", "CircleCheck", "Total Batches", "#10B981", change_text="Completed", is_positive=True)
            with c3:
                render_kpi_card("Failed Tasks", f"{fail_count}", "CircleX", "Pipeline Errors", "#EF4444", change_text="Errors", is_positive=(fail_count == 0))
            with c4:
                render_kpi_card("Rows Inserted", f"{tot_rows:,}", "Database", "Incremental Rows", "#8B5CF6", change_text="Ingested", is_positive=True)
            with c5:
                render_kpi_card("Latest Watermark", latest_watermark.split()[0] if " " in latest_watermark else latest_watermark, "Clock", "High Watermark", "#06B6D4", change_text="Incremental", is_positive=True)

            st.divider()

            # Incremental Loading Telemetry Card
            latest_row = df_etl.iloc[0]
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('RotateCw', '#06B6D4', 18)} Incremental Loading Batch Telemetry</div>""", unsafe_allow_html=True)
            
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.metric("Batch ID", f"#{latest_row['batch_id']}")
            with i2:
                st.metric("Rows Read", f"{latest_row['rows_read']:,}")
            with i3:
                st.metric("Rows Inserted", f"{latest_row['rows_inserted']:,}")
            with i4:
                st.metric("Rows Rejected", f"{latest_row['rows_rejected']:,}")

            st.divider()

            # Charts: Status Distribution & Rows Ingested by Task
            r1_col1, r1_col2 = st.columns(2)
            with r1_col1:
                st.markdown(f"""<div class="saas-card-title">{get_icon_svg('PieChart', '#3B82F6', 18)} Batch Execution Status Breakdown</div>""", unsafe_allow_html=True)
                st_counts = df_etl["status"].value_counts().reset_index()
                st_counts.columns = ["status", "count"]
                render_donut_chart(st_counts, "status", "count", height=240)

            with r1_col2:
                st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#10B981', 18)} Rows Ingested per Batch</div>""", unsafe_allow_html=True)
                batch_rows = df_etl.head(15).copy()
                batch_rows["batch_label"] = batch_rows["batch_id"].apply(lambda b: f"Batch #{b}")
                render_bar_chart(batch_rows, "batch_label", "rows_inserted", color="#10B981", title="Rows Inserted", height=240)

            st.divider()

            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Workflow', '#3B82F6', 18)} Airflow DAG Batch Execution Log</div>""", unsafe_allow_html=True)
            
            df_etl_display = df_etl.copy()
            df_etl_display["status"] = df_etl_display["status"].apply(render_status_pill)
            st.dataframe(df_etl_display, use_container_width=True, hide_index=True)
            st.download_button("Download ETL Batch Log CSV", df_etl.to_csv(index=False), "etl_batch_log.csv", "text/csv")
        else:
            st.info("No ETL batch records found in audit.etl_batch_log.")
    except Exception as ex:
        st.error(f"Could not load Pipeline Health data: {ex}")
