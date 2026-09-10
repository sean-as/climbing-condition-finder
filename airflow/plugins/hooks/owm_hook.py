import os
import requests
from airflow.hooks.base import BaseHook


class OwmHook(BaseHook):

    source_name = "owm"
    forecast_api = "https://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, source_name: str = source_name, forecast_api: str = forecast_api, api_key: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_name = source_name
        self.forecast_api = forecast_api
        # TODO make this config driven / move to Airflow Connection instead of raw env var
        self.api_key = api_key or os.environ["OWM_API_KEY"]

    def get_hourly_forecast(self, area_id, lat, long) -> dict:
        params = {
            "lat": lat,
            "lon": long,
            "appid": self.api_key,
            "units": "imperial",   # match NWS units (F, mph) to simplify downstream unioning
        }
        try:
            response = requests.get(self.forecast_api, params=params)
            response.raise_for_status()
            data = response.json()
            self.log.info(f"Succesfully fetched OWM forecast for area_id: {area_id}")
        except requests.exceptions.RequestException:
            self.log.exception(f"OWM forecast request failed for area_id={area_id}, lat={lat}, long={long}")
            raise

        try:
            if not data.get("list"):
                raise ValueError("no forecast periods returned")
            return {"data": data, "area_id": area_id}
        except (KeyError, TypeError, ValueError):
            self.log.error(f"Unexpected/empty OWM forecast for area_id={area_id}: {data}")
            raise
