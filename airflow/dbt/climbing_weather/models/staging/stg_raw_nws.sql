with
    source as (select * from {{ source("raw_data", "raw_nws") }}),
    unnested as (
        select
            extracted_at_ts,
            json_value(data, '$.properties.generatedAt') as generated_at,
            json_query(data, '$.geometry') as geo_json,
            json_value(data, '$.properties.elevation.value') as elevation_value,
            json_value(data, '$.properties.elevation.unitCode') as elevation_unit,
            json_value(data, '$.properties.validTimes') as valid_period,
            periods
        from source, unnest(json_query_array(data, '$.properties.periods')) periods
    ),
    typed as (
        select
            extracted_at_ts,
            generated_at,
            geo_json,
            cast(elevation_value as numeric) as elevation_value,
            elevation_unit,
            valid_period,
            timestamp(json_value(periods, '$.startTime')) as start_time,
            timestamp(json_value(periods, '$.endTime')) as end_time,
            cast(json_value(periods, '$.temperature') as numeric) as temperature_value,
            json_value(periods, '$.temperatureUnit') as temperature_unit,
            cast(
                json_value(periods, '$.probabilityOfPrecipitation.value') as numeric
            ) as precipitation_probability_value,
            json_value(
                periods, '$.probabilityOfPrecipitation.unitCode'
            ) as precipitation_probability_unit,
            cast(json_value(periods, '$.dewpoint.value') as numeric) as dewpoint_value,
            json_value(periods, '$.dewpoint.unitCode') as dewpoint_unit,
            cast(
                json_value(periods, '$.relativeHumidity.value') as numeric
            ) as relative_humidity_value,
            json_value(
                periods, '$.relativeHumidity.unitCode'
            ) as relative_humidity_unit,
            cast(
                regexp_extract(json_value(periods, '$.windSpeed'), r'^(\d+)') as numeric
            ) as wind_speed_low,
            cast(
                array_reverse(
                    regexp_extract_all(json_value(periods, '$.windSpeed'), r'\d+')
                )[safe_offset(0)] as numeric
            ) as wind_speed_high,
            regexp_extract(
                json_value(periods, '$.windSpeed'), r'([a-zA-Z]+)\s*$'
            ) as wind_speed_unit,
            json_value(periods, '$.windDirection') as wind_direction,
            json_value(periods, '$.shortForecast') as short_forecast
        from unnested
    )
select *
from typed
