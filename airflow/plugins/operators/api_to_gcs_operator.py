from airflow.models import BaseOperator
from google.cloud import storage
from datetime import datetime, timezone
import json

class ApiToGcsOperator(BaseOperator):
    default_bucket = "climbing-weather-499816-raw-weather"

    def __init__(self,bucket: str = default_bucket, hook_cls=None, hook_kwargs=None, hook_method=None, hook_method_kwargs=None, push_to_xcom: bool=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket = bucket
        self.hook_cls = hook_cls
        self.hook_method = hook_method
        self.hook_kwargs = hook_kwargs
        self.hook_method_kwargs = hook_method_kwargs
        self.push_to_xcom = push_to_xcom

    def upload_to_gcs(self, json_data, destination_blob_name): 
        # TODO remove static project definition
        storage_client = storage.Client(project="climbing-weather-499816")
        bucket = storage_client.bucket(self.bucket)
        blob = bucket.blob(destination_blob_name)
        #TODO Make logging more verbose
        try: 
            blob.upload_from_string(
                data=json_data,
                content_type='application/json'
            )
        except Exception as e:
            self.log.exception('ERROR')
            raise


    def execute(self, context):
        hook = self.hook_cls(**(self.hook_kwargs or {}))
        data = getattr(hook, self.hook_method)(**(self.hook_method_kwargs or {}))  
        ingested_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(data, list):
            json_str = "\n".join(json.dumps({**obj, "airflow_run_ts": context["ts"], "ingested_at_ts": ingested_at}) for obj in data)
        else:
            json_str = json.dumps({**data, "airflow_run_ts": context["ts"], "ingested_at_ts": ingested_at})
        idx = context["ti"].map_index
        self.upload_to_gcs(json_str, f"raw_api/{hook.source_name}/{self.task_id}_{idx}_{context['ts_nodash']}.json")
        if self.push_to_xcom: 
            return data




