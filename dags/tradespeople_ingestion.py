"""Airflow DAG for loading source Parquet files from S3 into Snowflake."""

from __future__ import annotations

import os
from datetime import datetime

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.log import mask_secret


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise AirflowException(f"Missing required environment variable: {name}")
    return value


with DAG(
    dag_id="tradespeople_ingestion",
    description="Load source Parquet files from S3 into Snowflake.",
    start_date=datetime(2025, 4, 1),
    schedule="@daily",
    catchup=False,
    tags=["athena", "snowflake", "elt"],
    default_args={"retries": 0},
) as dag:
    aws_access_key_id = _require_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = _require_env("AWS_SECRET_ACCESS_KEY")
    mask_secret(aws_access_key_id)
    mask_secret(aws_secret_access_key)
    quote_packages_s3_path = _require_env("SOURCE_PARQUET_S3_PATH").rstrip("/") + "/quote_packages"

    stage_name = "SOURCE_PARQUET_STAGE"
    file_format_name = "SOURCE_PARQUET_FF"
    external_table_name = "SOURCE_PARQUET_EXT"
    target_table = "QUOTE_PACKAGES"
    updated_at_filter = "2000-01-01"

    load_quote_packages = SQLExecuteQueryOperator(
        task_id="quote_packages",
        conn_id="snowflake_sandbox_encoded",
        split_statements=True,
        sql=f"""
        CREATE OR REPLACE STAGE {stage_name}
        URL = '{quote_packages_s3_path}'
        CREDENTIALS = (
            AWS_KEY_ID = '{aws_access_key_id}'
            AWS_SECRET_KEY = '{aws_secret_access_key}'
        );

        CREATE OR REPLACE FILE FORMAT {file_format_name}
        TYPE = PARQUET;

        CREATE OR REPLACE EXTERNAL TABLE {external_table_name}
        USING TEMPLATE (
            SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
            FROM TABLE(
                INFER_SCHEMA(
                    LOCATION => '@{stage_name}',
                    FILE_FORMAT => '{file_format_name}',
                    IGNORE_CASE => TRUE
                )
            )
        )
        LOCATION = @{stage_name}
        AUTO_REFRESH = FALSE
        FILE_FORMAT = (FORMAT_NAME = '{file_format_name}');

        CREATE OR REPLACE TABLE {target_table} AS
        SELECT *
        FROM {external_table_name}
        WHERE UPDATED_AT >= TO_TIMESTAMP_NTZ('{updated_at_filter}');

        DROP EXTERNAL TABLE IF EXISTS {external_table_name};
        """,
    )
