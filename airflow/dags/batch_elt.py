from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG("batch_elt", start_date=datetime(2026, 1, 1), schedule="@daily",
         catchup=False, default_args={"retries": 3, "retry_delay": timedelta(minutes=5)}) as dag:
    ingest = BashOperator(task_id="ingest_raw", bash_command="python /opt/airflow/scripts/ingest.py --input /opt/airflow/data/orders.csv --database /opt/airflow/warehouse/warehouse.duckdb")
    build = BashOperator(task_id="dbt_build", bash_command="cd /opt/airflow && dbt build --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt")
    ingest >> build
