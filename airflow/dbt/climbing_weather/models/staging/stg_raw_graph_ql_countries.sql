with source as (select * from {{ source("raw_data", "raw_graph_ql_countries") }})

select areaname as country
from source
