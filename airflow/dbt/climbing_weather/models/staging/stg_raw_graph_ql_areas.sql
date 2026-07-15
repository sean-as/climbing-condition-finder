with source as (select * from {{ source("raw_data", "raw_graph_ql_areas") }})

select
    uuid as id,
    area_name,
    cast(json_value(metadata, '$.lat') as numeric) as latitude,
    cast(json_value(metadata, '$.lng') as numeric) as longitude,
    children,
    ancestors,
    pathtokens as path_array,
    cast(json_value(metadata, '$.leaf') as boolean) as is_leaf
from source
