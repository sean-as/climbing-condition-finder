from operators.api_to_gcs_operator import ApiToGcsOperator
from hooks.graphql_hook import GraphqlHook
from hooks.nws_hook import NwsHook
from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook


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
    dag_id = 'raw_climbing_areas_to_gcs', 
    start_date = datetime(2026, 6, 25),
    schedule="@weekly", 
    catchup=False,
    tags=["raw"],
)
def raw_climbing_areas_to_gcs():  
    open_beta_areas_to_gcs_operator = ApiToGcsOperator(task_id="ingest_open_beta_areas", hook_cls=GraphqlHook, hook_kwargs={'source_name': 'open_beta'}, hook_method='get_areas')
    open_beta_countries_to_gcs_operator = ApiToGcsOperator(task_id="ingest_open_beta_countries", hook_cls=GraphqlHook, hook_kwargs={'source_name': 'open_beta'}, hook_method='get_countries')

    areas_gcs_to_bq_operator = GCSToBigQueryOperator(
        task_id='raw_open_beta_areas_gcs_to_bq', 
        bucket='climbing-weather-499816-raw-weather', 
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects = ["raw_api/open_beta/ingest_open_beta_areas_*_{{ ts_nodash }}.json"],
        destination_project_dataset_table = "climbing_weather.raw_open_beta_areas",
        autodetect=False,
        schema_fields=[
            {"name": "uuid", "type": "STRING", "mode": "REQUIRED"},
            {"name": "area_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "areaName", "type": "STRING", "mode": "REQUIRED"},
            {"name": "pathTokens", "type": "STRING", "mode": "REPEATED"},
            {"name": "ancestors", "type": "STRING", "mode": "REPEATED"}, 
            {"name": "children", "type": "JSON"}, 
            {"name": "metadata", "type": "JSON", "mode": "REQUIRED"}, 
            {"name": "airflow_run_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}, 
            {"name": "ingested_at_ts", "type": "TIMESTAMP", "mode": "REQUIRED"},
        ],
        write_disposition="WRITE_APPEND",
    )

    countries_gcs_to_bq_operator = GCSToBigQueryOperator(
        task_id='raw_open_beta_countries_gcs_to_bq', 
        bucket='climbing-weather-499816-raw-weather', 
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects = ["raw_api/open_beta/ingest_open_beta_countries_*_{{ ts_nodash }}.json"], 
        destination_project_dataset_table = "climbing_weather.raw_open_beta_countries",
        autodetect=False,
        schema_fields=[
            {"name": "areaName", "type": "STRING", "mode": "REQUIRED"},
            {"name": "airflow_run_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}, 
            {"name": "ingested_at_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}
        ],
        write_disposition="WRITE_APPEND",
    )

    resolve_gridpoints = ApiToGcsOperator.partial(
        task_id="resolve_gridpoints",
        hook_cls=NwsHook,
        hook_method="resolve_gridpoint",
    ).expand(hook_method_kwargs=get_target_crags())

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
            {"name": "grid_y",      "type": "INTEGER",   "mode": "NULLABLE"}, 
            {"name": "airflow_run_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}, 
            {"name": "ingested_at_ts", "type": "TIMESTAMP", "mode": "REQUIRED"}
        ],
        write_disposition="WRITE_APPEND",
    )

    open_beta_areas_to_gcs_operator >> areas_gcs_to_bq_operator
    open_beta_countries_to_gcs_operator >> countries_gcs_to_bq_operator 
    resolve_gridpoints >> gridpoints_gcs_to_bq


dag = raw_climbing_areas_to_gcs()
