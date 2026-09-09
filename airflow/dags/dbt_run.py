from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from datetime import datetime

project_config = ProjectConfig("/opt/airflow/dbt/climbing_weather")
profile_config = ProfileConfig(
    profile_name="climbing_weather",
    target_name="dev",
    profiles_yml_filepath="/opt/airflow/.dbt/profiles.yml",
)
execution_config = ExecutionConfig(dbt_executable_path="/usr/local/bin/dbt")

dbt_run = DbtDag(
    project_config=project_config,
    profile_config=profile_config,
    schedule=None, # Triggered by raw_forecast_to_gcs
    execution_config=execution_config,
    start_date=datetime(2026, 6, 25),
    dag_id="dbt_run",
)