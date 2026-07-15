from google.cloud import bigquery

from schemas.forecast import ForecastResponse, Point, Series
from services.bq_client import get_client


METRICS = {
    "temperature":        [("nws", "temperature_value",               "temperature_unit")],
    "wind_speed":         [("low",  "wind_speed_low",  "wind_speed_unit"),
                           ("high", "wind_speed_high", "wind_speed_unit")],   # 2 lines, 1 chart
    "precip_probability": [("nws", "precipitation_probability_value", "precipitation_probability_unit")],
    "humidity":           [("nws", "relative_humidity_value",         "relative_humidity_unit")],
    "dewpoint":           [("nws", "dewpoint_value",                  "dewpoint_unit")],
}

QUERY = """
  select start_time, temperature_value, temperature_unit,
         wind_speed_low, wind_speed_high, wind_speed_unit,
         precipitation_probability_value, precipitation_probability_unit,
         relative_humidity_value, relative_humidity_unit,
         dewpoint_value, dewpoint_unit
  from `climbing_weather.fact_hourly_forecast_by_area`
  where area_id = @area_id
  and start_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  order by start_time desc
"""

def get_forecast(area_id: str) -> ForecastResponse:
    client = get_client()
    job = client.query(QUERY, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("area_id", "STRING", area_id)],
    ))
    rows = list(job.result())

    series: dict[str, list[Series]] = {}
    for metric, specs in METRICS.items():
        series[metric] = [
            Series(
                source="nws",
                label=label,
                unit=(rows[0][unit_col] if rows else None),
                points=[Point(t=r["start_time"], v=r[value_col]) for r in rows],
            )
            for (label, value_col, unit_col) in specs
        ]

    return ForecastResponse(area_id=area_id, series=series)