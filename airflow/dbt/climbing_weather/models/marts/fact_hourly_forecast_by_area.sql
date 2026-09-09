  {{ config(
      materialized='incremental',
      incremental_strategy='insert_overwrite',
      partition_by={'field': 'start_time', 'data_type': 'timestamp'},
      unique_key=['area_id', 'start_time']
  ) }}
with source as (select * from {{ ref("int_forecast_hourly_by_area") }})
select
    area_id,
    ingested_at_ts,
    generated_at,
    elevation_value,
    elevation_unit,
    valid_period,
    start_time,
    end_time,
    temperature_value,
    temperature_unit,
    precipitation_probability_value,
    precipitation_probability_unit,
    dewpoint_value,
    dewpoint_unit,
    relative_humidity_value,
    relative_humidity_unit,
    wind_speed_low,
    wind_speed_high,
    wind_speed_unit,
    wind_direction,
    short_forecast,
    {{
        climb_score(
            "temperature_value",
            "precipitation_probability_value",
            "wind_speed_high",
            "relative_humidity_value",
        )
    }} as climb_score
from
    source
{% if is_incremental() %}
  where ingested_at_ts > (select max(ingested_at_ts) from {{ this }})
{% endif %}
