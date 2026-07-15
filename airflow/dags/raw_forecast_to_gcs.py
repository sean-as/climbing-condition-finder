from operators.api_to_gcs_operator import ApiToGcsOperator
from hooks.nws_hook import NwsHook
from airflow.decorators import dag,  task
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from datetime import datetime
from airflow.operators.empty import EmptyOperator

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
    # TODO: Make first run able to handle missing raw_gridpoints
    hook = BigQueryHook(gcp_conn_id='google_cloud_default', use_legacy_sql=False, location='US')
    rows = hook.get_records(sql)          # list of tuples
    return [{"area_id": str(r[0]), "lat": str(r[1]), "long": str(r[2])} for r in rows]

@task
def get_distinct_gridpoints():
    sql = """
        select distinct grid_id, grid_x, grid_y
        from `climbing_weather.raw_gridpoints`
    """
    hook = BigQueryHook(gcp_conn_id="google_cloud_default", use_legacy_sql=False, location="US")
    rows = hook.get_records(sql)
    return [{"grid_id": r[0], "grid_x": int(r[1]), "grid_y": int(r[2])} for r in rows]

@dag(
    dag_id = 'raw_forecast_to_gcs', 
    start_date = datetime(2026, 6, 25),
    schedule="@daily", 
    catchup=False,
    tags=["raw"],
)
def raw_api_to_gcs():
    # TODO Placeholder to pull locations to dynamically create dag
    # Phase 1: Do LA Basin (5da0e075-8ec5-5ad3-8136-49a5d4dacaa5) and San Jacinto Mountains (7197701e-a308-5315-afe9-b29ace8a8565)
    # Split into separate DAGS because pulling target crags doesn't update at the same time
    start = EmptyOperator(task_id="start_pipeline")
    
    resolve_gripoints = ApiToGcsOperator.partial(
    task_id="resolve_gridpoints",
    hook_cls=NwsHook,
    hook_method="resolve_gridpoint",
    ).expand(hook_method_kwargs=get_target_crags())
    
    nws_hourly_forecast = ApiToGcsOperator.partial(
    task_id="ingest_nws_hourly_forecast",
    hook_cls=NwsHook,
    hook_method="get_hourly_forecast",
    ).expand(hook_method_kwargs=get_distinct_gridpoints())

    gridpoints_gcs_to_bq = GCSToBigQueryOperator(
        task_id="gridpoints_gcs_to_bq",
        bucket="climbing-weather-499816-raw-weather",
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects=["raw_api/nws/resolve_gridpoints_*_{{ ts_nodash }}.json"],  # task_id distinguishes from forecast files
        destination_project_dataset_table="climbing_weather.raw_gridpoints",
        autodetect=False,
        schema_fields=[
            {"name": "area_id",     "type": "STRING",    "mode": "REQUIRED"},
            {"name": "grid_id",     "type": "STRING",    "mode": "NULLABLE"},
            {"name": "grid_x",      "type": "INTEGER",   "mode": "NULLABLE"},
            {"name": "grid_y",      "type": "INTEGER",   "mode": "NULLABLE"}
        ],
        write_disposition="WRITE_APPEND",
    )

    nws_hourly_forecast_gcs_to_bq = GCSToBigQueryOperator(
        task_id="nws_hourly_forecast_gcs_to_bq",
        bucket="climbing-weather-499816-raw-weather",
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects=["raw_api/nws/ingest_nws_hourly_forecast*_{{ ts_nodash }}.json"],  # task_id distinguishes from forecast files
        destination_project_dataset_table="climbing_weather.raw_nws",
        autodetect=False,
        schema_fields=[
            {"name":"data","type":"JSON","mode":"REQUIRED"},
            {"name":"extracted_at_ts","type":"TIMESTAMP","mode":"REQUIRED"}
        ],
        write_disposition="WRITE_APPEND",
    )

    start >> resolve_gripoints >> gridpoints_gcs_to_bq >> nws_hourly_forecast >> nws_hourly_forecast_gcs_to_bq





dag = raw_api_to_gcs()


