import csv
import os
from datetime import datetime, timedelta

from airflow.sdk import dag, task

ACCOUNT = os.environ["SNOWFLAKE_ACCOUNT"]
USER = os.environ["SNOWFLAKE_USER"]
KEY_PATH = "/opt/airflow/config/snowflake_key.p8"
EXPORT_DIR = "/opt/airflow/config/export"
STAGE = "@CLAIMS_DB.GOLD.EXPORTS_STAGE"

TABLES = {
    "DIM_PATIENT": "dim_patient.csv",
    "DIM_PROVIDER": "dim_provider.csv",
    "DIM_PAYER": "dim_payer.csv",
    "DIM_DIAGNOSIS": "dim_diagnosis.csv",
    "DIM_DATE": "dim_date.csv",
    "FACT_CLAIMS": "fact_claims.csv",
}


def get_conn():
    import snowflake.connector
    from cryptography.hazmat.primitives import serialization

    with open(KEY_PATH, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    der = key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return snowflake.connector.connect(
        account=ACCOUNT, user=USER, private_key=der,
        role="CLAIMS_LOADER", warehouse="CLAIMS_WH",
        database="CLAIMS_DB", schema="GOLD",
    )


def log_run(status, message=""):
    """Write one row to the run log table in Snowflake."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS CLAIMS_DB.GOLD.PIPELINE_RUN_LOG ("
            "run_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(), "
            "dag_id STRING, status STRING, message STRING)")
        cur.execute(
            "INSERT INTO CLAIMS_DB.GOLD.PIPELINE_RUN_LOG (dag_id, status, message) "
            "VALUES (%s, %s, %s)",
            ("claims_pipeline", status, message[:1000]))
    finally:
        conn.close()


def on_failure(context):
    """Runs after a task fails for good (all retries used)."""
    try:
        ti = context["task_instance"]
        log_run("FAILED", f"task={ti.task_id}")
    except Exception as e:
        print("Could not write failure to the run log:", e)


@dag(
    dag_id="claims_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",               # every day at 06:00 UTC (11:30 AM India time)
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
        "execution_timeout": timedelta(minutes=15),
        "on_failure_callback": on_failure,
    },
    tags=["claims", "snowflake"],
)
def claims_pipeline():

    @task
    def check_files() -> dict:
        expected = {}
        for table, fname in TABLES.items():
            path = os.path.join(EXPORT_DIR, fname)
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                raise FileNotFoundError(f"Missing or empty file: {path}")
            with open(path, newline="", encoding="utf-8") as f:
                rows = sum(1 for _ in csv.reader(f)) - 1
            expected[table] = rows
            print(f"{fname}: {rows} rows")
        return expected

    @task
    def upload_to_stage(expected: dict) -> dict:
        conn = get_conn()
        try:
            cur = conn.cursor()
            for fname in TABLES.values():
                path = os.path.join(EXPORT_DIR, fname)
                cur.execute(
                    f"PUT file://{path} {STAGE} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
                print("uploaded", fname)
        finally:
            conn.close()
        return expected

    @task
    def load_tables(expected: dict) -> dict:
        conn = get_conn()
        try:
            cur = conn.cursor()
            for table, fname in TABLES.items():
                cur.execute(f"TRUNCATE TABLE CLAIMS_DB.GOLD.{table}")
                cur.execute(
                    f"COPY INTO CLAIMS_DB.GOLD.{table} FROM {STAGE}/{fname} "
                    f"FORCE = TRUE ON_ERROR = 'ABORT_STATEMENT'")
                print("loaded", table)
        finally:
            conn.close()
        return expected

    @task
    def quality_checks(expected: dict):
        conn = get_conn()
        failures = []
        try:
            cur = conn.cursor()
            for table, exp in expected.items():
                cur.execute(f"SELECT COUNT(*) FROM CLAIMS_DB.GOLD.{table}")
                got = cur.fetchone()[0]
                status = "OK" if got == exp else "MISMATCH"
                print(f"{table}: file={exp} snowflake={got} {status}")
                if got != exp:
                    failures.append(f"{table} count {got} != {exp}")

            checks = {
                "duplicate encounter_id in FACT_CLAIMS":
                    "SELECT COUNT(*) - COUNT(DISTINCT encounter_id) FROM CLAIMS_DB.GOLD.FACT_CLAIMS",
                "null keys in FACT_CLAIMS":
                    "SELECT COUNT_IF(encounter_id IS NULL OR patient_id IS NULL) FROM CLAIMS_DB.GOLD.FACT_CLAIMS",
                "claims with unknown patient":
                    "SELECT COUNT(*) FROM CLAIMS_DB.GOLD.FACT_CLAIMS f "
                    "LEFT JOIN CLAIMS_DB.GOLD.DIM_PATIENT p ON f.patient_id = p.patient_id "
                    "WHERE p.patient_id IS NULL",
            }
            for label, sql in checks.items():
                cur.execute(sql)
                bad = cur.fetchone()[0]
                print(f"{label}: {bad}")
                if bad != 0:
                    failures.append(f"{label}: {bad}")
        finally:
            conn.close()
        if failures:
            raise ValueError("Quality checks failed: " + "; ".join(failures))
        print("All quality checks passed")

    @task
    def log_success():
        log_run("SUCCESS", "all tasks and quality checks passed")

    qc = quality_checks(load_tables(upload_to_stage(check_files())))
    qc >> log_success()


claims_pipeline()