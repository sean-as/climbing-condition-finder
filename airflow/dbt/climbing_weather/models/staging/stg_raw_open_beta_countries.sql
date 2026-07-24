with source as (select * from {{ source("raw_data", "raw_open_beta_countries") }})

select areaname as country
from source
