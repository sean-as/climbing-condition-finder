with
    stg_raw_nws as (select * from {{ ref("stg_raw_nws") }}),
    int_area_hierarchy as (select * from {{ ref("int_area_hierarchy") }}),
    geo_joined as (
        select
            area.id as area_id,
            nws.extracted_at_ts,
            nws.generated_at,
            nws.elevation_value,
            nws.elevation_unit,
            nws.valid_period,
            nws.start_time,
            nws.end_time,
            nws.temperature_value,
            nws.temperature_unit,
            nws.precipitation_probability_value,
            nws.precipitation_probability_unit,
            nws.dewpoint_value,
            nws.dewpoint_unit,
            nws.relative_humidity_value,
            nws.relative_humidity_unit,
            nws.wind_speed_low,
            nws.wind_speed_high,
            nws.wind_speed_unit,
            nws.wind_direction,
            nws.short_forecast
        from stg_raw_nws nws
        join
            int_area_hierarchy area
            on st_contains(
                st_geogfromgeojson(to_json_string(geo_json), make_valid => true),
                st_geogpoint(longitude, latitude)
            )
        qualify
            row_number() over (
                partition by area.id, nws.start_time order by nws.generated_at desc
            )
            = 1
    )
select *
from geo_joined
