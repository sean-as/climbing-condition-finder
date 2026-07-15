{% macro ramp(x, cutoff, ideal) %}
    greatest(0, least(1, ({{ x }} - {{ cutoff }}) / ({{ ideal }} - {{ cutoff }})))
{% endmacro %}
