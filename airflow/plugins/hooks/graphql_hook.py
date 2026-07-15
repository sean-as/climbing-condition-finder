import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from airflow.hooks.base import BaseHook
from datetime import datetime, timezone
import json


class GraphqlHook(BaseHook): 
    
    source_name = "graph_ql"
    # TODO make this config driven to allow for other sources
    endpoint = 'https://api.openbeta.io'
    def __init__(self, source_name: str = source_name, endpoint: str = endpoint, auth_key = None,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_name = source_name
        self.endpoint = endpoint
        self.auth_key = auth_key


    def get_countries(self): 
        COUNTRIES_QUERY = """
        query GetCountries {
        countries {
            areaName
        }
        }
        """
        try:
            response = requests.post(
                self.endpoint,
                json={"query": COUNTRIES_QUERY},
                headers={"Content-Type": "application/json"},
                timeout=60,
                )
            response.raise_for_status()
            contries = response.json().get("data", {}).get("countries", [])
            self.log.info(contries)
            return "\n".join(json.dumps(obj) for obj in contries)

        except requests.exceptions.RequestException: 
            self.log.exception(f"Request Exception: Unable to fetch countries from Open Beta")
            raise

    def get_areas(self): 
        import time, random
        AREAS_QUERY = """
            query GetAreas($limit: Int!, $offset: Int!) {
            areas(limit: $limit, offset: $offset) {
                uuid
                area_name
                areaName
                ancestors
                pathTokens
                children {
                area_name
                uuid
                }
                metadata {
                lat
                lng
                leaf
                }
            }
            }

        """
        limit = 500
        offset = 0 
        area_list = []
        areas = []

        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=3,
            status_forcelist=[502],
            allowed_methods=['POST']
        )
        custom_adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", custom_adapter)
        while True: 
            try:
                response = session.post(
                    self.endpoint,
                    json={"query": AREAS_QUERY,
                        "variables": {
                            "limit": limit,
                            "offset": offset
                        }},
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                    )
                data = response.json()
                self.log.info(f"Number of pages fetches so far: {offset / limit}")
                areas = data.get("data", {}).get("areas", [])
                area_list.extend(areas)
                offset += limit
                time.sleep(1 + random.uniform(0, 0.5))
                if len(areas) < limit: 
                    # Last Page or no results returned break loop
                    break
            except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError): 
                self.log.exception(response.text)
                self.log.exception(f"Request Exception: Unable to fetch areas from Open Beta")
                raise
        return "\n".join(json.dumps(obj) for obj in area_list)