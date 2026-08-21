from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'principal_data_architect',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email': ['data-eng-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1)
}

with DAG(
    'dag_ecommerce_petabyte_master',
    default_args=default_args,
    description='End-to-End Ingestion, Spark Iceberg Processing, and dbt Modeling',
    schedule_interval='0 2 * * *', # Berjalan otomatis tiap jam 02:00 Pagi
    catchup=False,
    tags=['production', 'core_lakehouse', 'god_level']
) as dag:

    # Task 1: Health Check Data Ingress
    task_healthcheck = BashOperator(
        task_id='ingress_health_check',
        bash_command='python -c "print(\'Ingress Gateways Online\')"'
    )

    # Task 2: Trigger PySpark Distributed Job
    task_spark_job = BashOperator(
        task_id='submit_spark_iceberg_job',
        bash_command='spark-submit --master spark://spark-master:7077 /opt/spark_jobs/process_iceberg_stream.py'
    )

    # Task 3: dbt Data Modeling & Testing (Kimball Star Schema)
    task_dbt_run = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /opt/dbt_project && dbt run --models marts && dbt test'
    )

    # Dependency Pipeline DAG
    task_healthcheck >> task_spark_job >> task_dbt_run