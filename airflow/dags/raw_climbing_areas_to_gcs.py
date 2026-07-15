from operators.api_to_gcs_operator import ApiToGcsOperator
from hooks.graphql_hook import GraphqlHook
from airflow.decorators import dag
from datetime import datetime
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator


@dag(
    dag_id = 'raw_climbing_areas_to_gcs', 
    start_date = datetime(2026, 6, 25),
    schedule="@weekly", 
    catchup=False,
    tags=["raw"],
)
def raw_climbing_areas_to_gcs():
    # TODO Placeholder to pull locations to dynamically create dag
    start = EmptyOperator(task_id="start_pipeline")


    graph_ql_areas_to_gcs_operator = ApiToGcsOperator(task_id="ingest_graphql_areas", hook_cls=GraphqlHook, hook_method='get_areas')
    graph_ql_countries_to_gcs_operator = ApiToGcsOperator(task_id="ingest_graphql_countries", hook_cls=GraphqlHook, hook_method='get_countries')

    areas_gcs_to_bq_operator = GCSToBigQueryOperator(
        task_id='raw_graph_ql_areas_gcs_to_bq', 
        bucket='climbing-weather-499816-raw-weather', 
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects = ["raw_api/graph_ql/ingest_graphql_areas*.json"], # TODO Make this incremental only do newly fetched data
        destination_project_dataset_table = "climbing_weather.raw_graph_ql_areas",
        autodetect=False,
        schema_fields=[{"name": "uuid", "type": "STRING", "mode": "REQUIRED"}, {"name": "area_name", "type": "STRING", "mode": "REQUIRED"}, {"name": "areaName", "type": "STRING", "mode": "REQUIRED"}, {"name": "pathTokens", "type": "STRING", "mode": "REPEATED"}, {"name": "ancestors", "type": "STRING", "mode": "REPEATED"}, {"name": "children", "type": "JSON"}, {"name": "metadata", "type": "JSON", "mode": "REQUIRED"}],
        write_disposition="WRITE_TRUNCATE",
    )

    countries_gcs_to_bq_operator = GCSToBigQueryOperator(
        task_id='raw_graph_ql_countries_gcs_to_bq', 
        bucket='climbing-weather-499816-raw-weather', 
        source_format="NEWLINE_DELIMITED_JSON",
        source_objects = ["raw_api/graph_ql/ingest_graphql_countries_*.json"], # TODO Make this incremental only do newly fetched data
        destination_project_dataset_table = "climbing_weather.raw_graph_ql_countries",
        autodetect=False,
        schema_fields=[{"name": "areaName", "type": "STRING", "mode": "REQUIRED"}],
        write_disposition="WRITE_TRUNCATE",
    )
    start >> [graph_ql_areas_to_gcs_operator >> areas_gcs_to_bq_operator, graph_ql_countries_to_gcs_operator >> countries_gcs_to_bq_operator] 


dag = raw_climbing_areas_to_gcs()


