with
    source as (select * from {{ ref("stg_raw_graph_ql_areas") }}),
    hierarchy as (
        select
            id,
            latitude,
            longitude,
            area_name,
            ancestors[safe_offset(array_length(ancestors) - 2)] parent_id,
            path_array[safe_offset(0)] as country,
            path_array[safe_offset(1)] as region,
            is_leaf
        from source
    )

select *
from hierarchy
