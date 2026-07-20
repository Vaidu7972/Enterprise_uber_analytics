from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

default_args = {
    "owner": "vaidehi",
}

with DAG(
    dag_id="enterprise_uber_analytics_pipeline",
    default_args=default_args,
    description="Enterprise Uber Analytics Data Pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["uber", "analytics", "airflow", "docker"],
) as dag:

    load_trip_data = BashOperator(
        task_id="load_trip_data",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.ingestion.load_trip_data",
    )

    load_drivers = BashOperator(
        task_id="load_drivers",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.ingestion.load_drivers",
    )

    load_customers = BashOperator(
        task_id="load_customers",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.ingestion.load_customers",
    )

    load_weather = BashOperator(
        task_id="load_weather",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.ingestion.load_weather",
    )

    transform_trip_data = BashOperator(
        task_id="transform_trip_data",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.transformations.transform_trip_data",
    )

    transform_master_data = BashOperator(
        task_id="transform_master_data",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.transformations.transform_master_data",
    )

    create_trip_enriched = BashOperator(
        task_id="create_trip_enriched",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.transformations.create_trip_enriched",
    )

    load_dim_driver = BashOperator(
        task_id="load_dim_driver",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.warehouse.load_dim_driver",
    )

    load_dim_customer = BashOperator(
        task_id="load_dim_customer",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.warehouse.load_dim_customer",
    )

    load_dim_weather = BashOperator(
        task_id="load_dim_weather",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.warehouse.load_dim_weather",
    )

    load_dim_date = BashOperator(
        task_id="load_dim_date",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.warehouse.load_dim_date",
    )

    load_fact_trip = BashOperator(
        task_id="load_fact_trip",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.warehouse.load_fact_trip",
    )

    load_analytics_marts = BashOperator(
        task_id="load_analytics_marts",
        bash_command=f"cd {PROJECT_DIR} && python -m scripts.warehouse.load_analytics_marts",
    )

    # Ingestion dependencies
    load_trip_data >> transform_trip_data
    load_drivers >> transform_master_data
    load_customers >> transform_master_data
    load_weather >> transform_master_data

    # Transformation dependencies
    transform_trip_data >> create_trip_enriched
    transform_master_data >> create_trip_enriched

    # Gold dimension dependencies
    create_trip_enriched >> load_dim_driver
    create_trip_enriched >> load_dim_customer
    create_trip_enriched >> load_dim_weather
    create_trip_enriched >> load_dim_date

    # Fact table dependencies
    load_dim_driver >> load_fact_trip
    load_dim_customer >> load_fact_trip
    load_dim_weather >> load_fact_trip
    load_dim_date >> load_fact_trip

    # Analytics mart dependency
    load_fact_trip >> load_analytics_marts