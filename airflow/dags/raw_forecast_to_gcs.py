from operators.api_to_gcs_operator import ApiToGcsOperator
from hooks.nws_hook import NwsHook
from hooks.owm_hook import OwmHook
from airflow.decorators import dag,  task
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from datetime import datetime
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

@task
def get_gridpoints():
    sql = """
        select area_id, grid_id, grid_x, grid_y
        from `climbing_weather.raw_gridpoints`
        qualify row_number() over (partition by area_id order by ingested_at_ts desc) = 1
    """
    # TODO: Make first run able to handle missing raw_gridpoints
    hook = BigQueryHook(gcp_conn_id='google_cloud_default', use_legacy_sql=False, location='US')
    rows = hook.get_records(sql)          # list of tuples
    return [{"area_id": str(r[0]), "grid_id": str(r[1]), "grid_x": r[2], "grid_y": r[3]} for r in rows]

@task
def get_target_crags():
    sql = """
        select id as area_id, latitude, longitude
        from `climbing_weather.dim_area`
        where parent_id in (
            '5da0e075-8ec5-5ad3-8136-49a5d4dacaa5',
            '7197701e-a308-5315-afe9-b29ace8a8565'
        )
        and area_name <> 'Beaches' -- Exclude because NWS cannot fetch weather for locations in the ocean
    """
    # TODO: Make first run able to handle missing dim_area
    hook = BigQueryHook(gcp_conn_id='google_cloud_default', use_legacy_sql=False, location='US')
    rows = hook.get_records(sql)          # list of tuples
    return [{"area_id": str(r[0]), "lat": str(r[1]), "long": str(r[2])} for r in rows]

@dag(
    dag_id = 'raw_forecast_to_gcs', 
    start_date = datetime(2026, 6, 25),
    schedule="@daily", 
    catchup=False,
    tags=["raw"],
)
def raw_api_to_gcs():
    # Phase 1: Do LA Basin (5da0e075-8ec5-5ad3-8136-49a5d4dacaa5) and San Jacinto Mountains (7197701e-a308-5315-afe9-b29ace8a8565)
    # Gridpoints are resolved weekly in raw_climbing_areas_to_gcs; a crag's gridpoint never changes
    start = EmptyOperator(task_id="start_pipeline")

    nws_hourly_forecast = ApiToGcsOperator.partial(
    task_id="ingest_nws_hourly_forecast",
    hook_cls=NwsHook,
    hook_method="get_hourly_forecast",
    ).expand(hook_method_kwargs=get_gridpoints())

    nws_hourly_forecast_gcs_to_bq = GCSToBigQueryOperator(
        task_id="nws_hourly_forecast_gcs_to_bq",
        bucket="climbing-weather-499816-raw-weather",
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects=["raw_api/nws/ingest_nws_hourly_forecast*_{{ ts_nodash }}.json"],  # task_id distinguishes from forecast files
        destination_project_dataset_table="climbing_weather.raw_nws",
        autodetect=False,
        schema_fields=[
            {"name":"data","type":"JSON","mode":"REQUIRED"},
            {"name": "airflow_run_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}, 
            {"name": "ingested_at_ts", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name":"area_id","type":"STRING","mode":"REQUIRED"}
        ],
        write_disposition="WRITE_APPEND",
    )

    owm_hourly_forecast = ApiToGcsOperator.partial(
    task_id="ingest_owm_hourly_forecast",
    hook_cls=OwmHook,
    hook_method="get_hourly_forecast",
    ).expand(hook_method_kwargs=get_target_crags())

    owm_hourly_forecast_gcs_to_bq = GCSToBigQueryOperator(
        task_id="owm_hourly_forecast_gcs_to_bq",
        bucket="climbing-weather-499816-raw-weather",
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects=["raw_api/owm/ingest_owm_hourly_forecast*_{{ ts_nodash }}.json"],  # task_id distinguishes from forecast files
        destination_project_dataset_table="climbing_weather.raw_owm",
        autodetect=False,
        schema_fields=[
            {"name":"data","type":"JSON","mode":"REQUIRED"},
            {"name": "airflow_run_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}, 
            {"name": "ingested_at_ts", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name":"area_id","type":"STRING","mode":"REQUIRED"}
        ],
        write_disposition="WRITE_APPEND",
    )

    trigger_dbt = TriggerDagRunOperator(
      task_id="trigger_dbt_run",
      trigger_dag_id="dbt_run",       # must match dag_id in your dbt_run.py DbtDag
      wait_for_completion=False,       # True if you want ingestion DAG to block until dbt finishes
    )

    start >> nws_hourly_forecast >> nws_hourly_forecast_gcs_to_bq >> trigger_dbt
    start >> owm_hourly_forecast >> owm_hourly_forecast_gcs_to_bq >> trigger_dbt


dag = raw_api_to_gcs()
