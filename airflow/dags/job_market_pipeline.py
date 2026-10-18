"""Pipeline quotidien : ingestion France Travail → dbt Silver → extraction IA → dbt Gold."""

from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PROJECT_DIR = "/opt/project"
DBT = f"cd {PROJECT_DIR}/transformation && dbt build --profiles-dir ."

with DAG(
    dag_id="job_market_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
    tags=["job_market"],
):
    ingest = BashOperator(
        task_id="ingest_france_travail",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.main_ingest",
    )
    silver = BashOperator(task_id="dbt_silver", bash_command=f"{DBT} --select silver")
    extract_skills = BashOperator(
        task_id="extract_skills",
        bash_command=f"cd {PROJECT_DIR} && python -m ai.extractor",
    )
    gold = BashOperator(task_id="dbt_gold", bash_command=f"{DBT} --select gold")

    ingest >> silver >> extract_skills >> gold
