from schemas.areas import AreaRef, AreaNode, AreaResponse
from services.bq_client import get_client
from google.cloud import bigquery

def get_area(id: str) -> AreaResponse:
    client = get_client()

    node_rows = list(client.query(
        "select id, area_name, latitude, longitude, parent_id, country, region, "
        "is_leaf "
        "from `climbing_weather.dim_area` where id = @id",
        job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", id)],
    ),
    ).result())
    if not node_rows:
        return None                       # router -> 404
    n = node_rows[0]

    children = [AreaRef(id=r["id"], area_name=r["area_name"]) for r in client.query(
        "select id, area_name from `climbing_weather.dim_area` "
        "where parent_id = @id order by area_name",
        job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", id)],
    ),
    ).result()]

    return AreaResponse(node=AreaNode(**{k: n[k] for k in AreaNode.model_fields}), children=children)
