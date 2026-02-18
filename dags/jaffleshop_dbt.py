"""Airflow DAG for running dbt on the jaffle_shop project."""
from datetime import datetime
from pathlib import Path

from cosmos import DbtDag, ProjectConfig, ProfileConfig
from cosmos.profiles import SnowflakePrivateKeyPemProfileMapping

from config import venv_execution_config

dbt_cosmos_dag = DbtDag(
    project_config=ProjectConfig(Path(__file__).parent / "dbt" / "jaffle_shop"),
    profile_config=ProfileConfig(
        profile_name="snowflake_sandbox_profile",
        target_name="snowflake_sandbox",
        profile_mapping=SnowflakePrivateKeyPemProfileMapping(
            conn_id="snowflake_sandbox"
        ),
    ),
    execution_config=venv_execution_config,
    schedule="@daily",
    start_date=datetime(2025, 4, 1),
    catchup=False,
    dag_id="jaffleshop_dbt",
    max_active_tasks=4,
    max_active_runs=1,
    is_paused_upon_creation=False,
    tags=["dbt","snowflake"]
)
