with
    source as (select * from {{ source("owm", "raw_owm") }}),
    unnested as (
        select
            ingested_at_ts,
            area_id,
            periods
        from source, unnest(json_query_array(data, '$.list')) periods
    ),
    typed as (
        select
            ingested_at_ts,
            area_id,
            timestamp_seconds(cast(json_value(periods, '$.dt') as int64)) as start_time,
            cast(json_value(periods, '$.main.temp') as numeric) as temperature_value,
            'F' as temperature_unit,
            cast(json_value(periods, '$.main.humidity') as numeric) as relative_humidity_value,
            '%' as relative_humidity_unit,
            cast(json_value(periods, '$.wind.speed') as numeric) as wind_speed_value,
            'mph' as wind_speed_unit,
            cast(json_value(periods, '$.pop') as numeric) * 100 as precipitation_probability_value,
            '%' as precipitation_probability_unit,
            cast(json_value(periods, '$.clouds.all') as numeric) as cloud_cover_value,
            '%' as cloud_cover_unit
        from unnested
    )
select *
from typed
