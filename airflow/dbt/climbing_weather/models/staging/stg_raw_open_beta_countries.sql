with source as (select * from {{ source("open_beta", "raw_open_beta_countries") }})

select areaname as country, airflow_run_ts, ingested_at_ts
from source
qualify ROW_NUMBER() over(partition by areaname order by airflow_run_ts desc, ingested_at_ts desc) = 1
