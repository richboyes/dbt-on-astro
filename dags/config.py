"Contains constants used in the DAGs"

from pathlib import Path
from cosmos import ExecutionConfig, ExecutionMode


dbt_executable = Path("/usr/local/airflow/dbt_venv/bin/dbt")

if dbt_executable.exists():

    # This means we are running locally
    venv_execution_config = ExecutionConfig(
        dbt_executable_path=str(dbt_executable),
    )
else:
    venv_execution_config = ExecutionConfig(
        execution_mode=ExecutionMode.LOCAL,
    )
