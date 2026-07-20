FROM apache/airflow:2.10.5-python3.12

USER airflow

COPY requirements-docker.txt /requirements-docker.txt

RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.12.txt" \
    -r /requirements-docker.txt