with source as (select * from {{ ref("int_area_hierarchy") }})
select
    id,
    if(
        area_name like '%, The',
        concat('The ', regexp_replace(area_name, ', The$', '')),
        area_name
    ) as area_name,
    latitude,
    longitude,
    parent_id,
    country,
    region,
    is_leaf
from source
