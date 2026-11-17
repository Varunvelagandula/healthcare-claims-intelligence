from datetime import datetime, timedelta
from airflow.sdk import dag, task


@dag(
    dag_id="claims_test_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=1)},
    tags=["claims", "test"],
)
def claims_test_pipeline():

    @task
    def export_gold():
        print("Step 1: export Gold tables from Databricks (placeholder)")
        return "exported"

    @task
    def load_snowflake(status: str):
        print(f"Step 2: load into Snowflake (placeholder), previous step: {status}")
        return "loaded"

    @task
    def run_quality_checks(status: str):
        print(f"Step 3: data quality checks (placeholder), previous step: {status}")

    run_quality_checks(load_snowflake(export_gold()))


claims_test_pipeline()