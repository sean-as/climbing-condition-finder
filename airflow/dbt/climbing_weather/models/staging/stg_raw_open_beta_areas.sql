with source as (select * from {{ source("open_beta", "raw_open_beta_areas") }})

select
    uuid as id,
    area_name,
    cast(json_value(metadata, '$.lat') as numeric) as latitude,
    cast(json_value(metadata, '$.lng') as numeric) as longitude,
    children,
    ancestors,
    pathtokens as path_array,
    cast(json_value(metadata, '$.leaf') as boolean) as is_leaf, 
    ingested_at_ts, 
    airflow_run_ts
from source
qualify ROW_NUMBER() over(partition by uuid order by airflow_run_ts desc, ingested_at_ts desc) = 1
