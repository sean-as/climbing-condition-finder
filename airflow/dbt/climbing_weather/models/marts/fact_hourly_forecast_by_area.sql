with source as (select * from {{ ref("int_forecast_hourly_by_area") }})
select
    area_id,
    extracted_at_ts,
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

    -- ## dbt polish — come back to
    -- ### Altitude / cleanup
    -- - [ ] fact_hourly_forecast_by_area: give it real mart value (climb-score, unit
    -- standardization) or accept it's just the read-layer — stop duplicating int
    -- - [ ] dbt_project.yml: set `intermediate: +materialized: view` explicitly
    -- - [ ] int_forecast_hourly_by_area:30 — qualify `nws.geo_json` in join
    -- - [ ] int_area_hierarchy:9 — add `AS` before `parent_id`
    -- ### Docs / tests (new models have none)
    -- - [ ] int_forecast_hourly_by_area.yml — columns + not_null(area_id, start_time)
    -- - [ ] fact_hourly_forecast_by_area.yml — unique(area_id, start_time)
    -- - [ ] stg_raw_nws.yml — add 14 metric cols, rename geo → geo_json, drop `periods`
    -- ### Bigger (not polish — schedule real time)
    -- - [ ] Thread grid_id/x/y through stg_raw_nws → join forecast↔area on gridpoint
    -- equality, demote ST_CONTAINS to a validation test
    -- - [ ] Move point-in-polygon to resolution/dim grain (1 check per crag, not per
    -- hour)
    -- - [ ] Standardize units in staging (temp F→C, wind range parse)
