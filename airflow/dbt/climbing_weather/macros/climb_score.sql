{% macro climb_score(temp, precip, wind, humid) %}
    -- Will need to refine these and determine how to weight, currently used simple AHP to do so
    {% set w_temp  = var('climb_w_temp', 0.60) %}
    {% set w_wind  = var('climb_w_wind', 0.20) %}
    {% set w_humid = var('climb_w_humid', 0.20) %}

    {% set wind_cutoff  = var('wind_high', 35) %}
    {% set wind_ideal  = var('wind_high', 25) %}
    
    {% set humidity_cutoff  = var('humidity_cutoff', 60) %}

    {% set temp_ideal_low = var('temp_ideal_low', 40) %}
    {% set temp_ideal_high = var('temp_ideal_high', 70) %}
    {% set temp_cutoff_low  = var('temp_cutoff_low', 30) %}
    {% set temp_cutoff_high  = var('temp_cutoff_high', 80) %}
    
    100
    * (1 - coalesce({{ precip }}, 0) / 100)
    * (
            case
                when {{ temp }} between {{ temp_ideal_low }} and {{ temp_ideal_high }} then 1.0
                when {{ temp }} <= {{ temp_cutoff_low }} or {{ temp_cutoff_high }} >= {{ temp }} then 0.0
                when {{ temp }} < {{ temp_ideal_low }} then {{ ramp(temp, temp_cutoff_low, temp_ideal_low) }}
                when {{ temp }} > {{ temp_ideal_high }} then {{ ramp(temp, temp_cutoff_high, temp_ideal_high) }}
            end
        )
      + {{ w_wind }}  * least({{ ramp(wind, wind_cutoff, wind_ideal) }}, {{ ramp(wind, 3, wind_ideal) }})
      + {{ w_humid }} * {{ ramp(humid, humidity_cutoff, 0) }}
{% endmacro %}