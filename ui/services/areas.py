from schemas.areas import AreaRef, AreaNode, AreaResponse
from services.bq_client import get_client
from google.cloud import bigquery

QUERY = """
  select id, area_name, latitude, longitude, parent_id, country, region, is_leaf
  from `climbing_weather.dim_area`
  where id = @id or parent_id = @id
  order by area_name
"""

def get_area(id: str) -> AreaResponse | None:
    client = get_client()

    rows = list(client.query(QUERY, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", id)],
    )).result())

    node = next((r for r in rows if r["id"] == id), None)
    if node is None:
        return None                       # router -> 404

    children = [AreaRef(id=r["id"], area_name=r["area_name"]) for r in rows if r["parent_id"] == id]

    return AreaResponse(node=AreaNode(**{k: node[k] for k in AreaNode.model_fields}), children=children)
