import requests
from airflow.hooks.base import BaseHook
from datetime import datetime, timezone
import json
class NwsHook(BaseHook): 

    source_name = "nws"
    # TODO Make this config driven and implement retries
    point_location_api = "https://api.weather.gov/points/" 
    grid_point_api = "https://api.weather.gov/gridpoints/"

    def __init__(self, source_name: str = source_name, point_location_api: str = point_location_api, grid_point_api: str = grid_point_api,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_name = source_name
        self.point_location_api = point_location_api
        self.grid_point_api = grid_point_api
    
    def resolve_gridpoint(self, area_id, lat, long): 
        url = f"{self.point_location_api}{lat},{long}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            grid_id = data["properties"]["gridId"]
            grid_x = data["properties"]["gridX"]
            grid_y = data["properties"]["gridY"]
            return {"area_id": area_id, "grid_id":grid_id, "grid_x":grid_x, "grid_y":grid_y}
        # TODO Catch KeyError or TypeError
        except requests.exceptions.RequestException:
             self.log.exception(f"NWS point location request failed for lat={lat}, long={long}")
             raise
            
    def get_hourly_forecast(self, grid_id, grid_x, grid_y):
        url = f"{self.grid_point_api}{grid_id}/{grid_x},{grid_y}/forecast/hourly"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.log.info(f"Succesfully fetched forecast for ...")
        # TODO Catch KeyError or TypeError, catch no forecast
            return json.dumps({"data": data, "extracted_at_ts": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
        except requests.exceptions.RequestException: 
             self.log.exception(f"NWS forecast request failed for grid_id={grid_id}, grid_x={grid_x}, grid_y={grid_y}")
             raise
