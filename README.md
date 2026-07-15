# Climbing Conditions

## Overview

A data pipeline and dashboard that answers "is Bishop climbable this weekend?", generating a conditon_score for each area and forecast based on temperature, precipitations, wind, and humidity levels. Rather than trusting a single forecast, there are multiple sources (NWS, open weather, etc.) and then eventually comparing against actual conditions. 

## Stack
- **Orchestration:** Airflow
- **Data Lake:** Google Cloud Storage 
- **Data Warehouse:** BigQuery 
- **Transformations:** dbt 
- **Dashboard:** FastAPI, ChartJS

---

## Diagram

```mermaid
flowchart TD
    subgraph Sources["Data Sources"]
        NWS["NWS API\n(US forecasts)"]
        OM["Open-Meteo API\n(global forecasts + actuals - only first 1000 calls are free)"]
        OWM["OpenWeatherMap API\n(forecasts)"]
        OB["OpenBeta API\n(climbing areas + routes)"]
    end

    subgraph Airflow["Orchestration — Airflow"]
        DAG1["raw_forecast_to_gcs DAG\n(daily)"]
        DAG2["raw_actuals_to_gcs DAG\n(daily, T+1)"]
        DAG3["raw_climbing_areas_to_gcs DAG\n(weekly seed)"]
        DAG4["dbt_run DAG\n(daily, after ingest)"]
    end

    subgraph GCS["GCS — Raw Layer"]
        GCS1["raw_api/nws/ingest_nws_hourly_forecast_*"]
        GCS2["raw_api/open_meteo/YYYY/MM/DD/"]
        GCS3["raw_api/openweathermap/YYYY/MM/DD/"]
        GCS4["raw_api/nws/YYYY/MM/DD/"]
        GCS5["raw_api/graph_ql/ingest_graphql_areas_*"]
        GCS6["raw_api/graph_ql/ingest_graphql_countries_*"]
    end

    subgraph BQ_Raw["BigQuery — Raw Tables"]
        BQR1["raw_nws"]
        BQR2["raw_open_meteo"]
        BQR3["raw_owm"]
        BQR4["raw_actuals"]
        BQR5["raw_gridpoints"]
        BQR6["raw_graph_ql_areas"]
        BQR7["raw_graph_ql_countries"]
    end

    subgraph DBT_Staging["dbt — Staging"]
        STG1["stg_raw_nws"]
        STG2["stg_actuals\n(normalized observations)"]
        STG3["stg_raw_graph_ql_areas\n(locations + metadata)"]
        STG4["stg_raw_graph_ql_countries\n(locations + metadata)"]
    end
    
    subgraph DBT_Intermediate["dbt — Intermediate"]
        INT1["int_forecasts__unioned"]
        INT2["int_area_hierarchy"]
        INT3["int_forecast_hourly_by_area"]
    end

    subgraph DBT_Marts["dbt — Marts (Gold)"]
        MART1["fact_hourly_forecast_by_area\n(condition score per crag per day)"]
        MART2["dim_area"]
        MART3["mart_forecast_accuracy\n(MAE by source, horizon, region)"]
    end

    subgraph Dashboard["Dashboard"]
        UI["Fast API"]
    end

    NWS --> DAG1
    OM --> DAG1
    OWM --> DAG1
    NWS --> DAG2
    OM --> DAG2
    OB --> DAG3

    DAG1 --> GCS1
    DAG1 --> GCS2
    DAG1 --> GCS3
    DAG2 --> GCS4
    DAG3 --> GCS5

    GCS1 -->|BQ Load Job| BQR1
    GCS2 -->|BQ Load Job| BQR2
    GCS3 -->|BQ Load Job| BQR3
    GCS4 -->|BQ Load Job| BQR4
    GCS5 -->|BQ Load Job| BQR5

    BQR1 --> INT1
    BQR2 --> INT1
    BQR3 --> INT1
    BQR4 --> INT1
    BQR5 --> INT1

    INT1 --> MART1
    INT1 --> MART2
    MART2 --> MART3

    MART1 --> UI
    MART3 --> UI

    DAG4 -.->|triggers| STG1
    DAG4 -.->|triggers| STG2
    DAG4 -.->|triggers| STG3
```

---

## Phases

| Phase | Deliverable | Status
|---|---|---|
| 1 | Run airflow locally using docker, set up intiial DBT models for NWS data and create condition_score, learn more about FastAPI to begin setting up UI | DONE
| 2 | Updated models to be incremental (forecast and areas). Remove get_distinct_gridpoints from ingestion of NWS to reduce BQ calls. Ensure naming patterns are aligned, rename graph_ql to openbeta.  Refine Charts in UI to make them more useable. Enable DBT to run in airflow. Resolve any other TODOs in codebase. | IN-PROGESS
| 3 | Add unit tests for airflow. Add second source Open Weather API. | TODO
| 4 | Deploy Airflow to cloud so it's updated more regularly. Add source for actualy temperature, humidity readings to compare models to forecast. | TODO
| 5 | Deploy UI to cloud run and set up appropriately in Terraform. | TODO

Additional things to consider: 
- FastAPI is slow with BQ queriy: BQ is meant for analytics so there is a couple second latency with page loading. Caching helps but alternatives are better. Things to consider: BQ to DuckDB file (could use up a lot of memory), Redis and Firestore (potentially overkill)



---

## Estimated Monthly Cost

Locally, using docker airflow and BQ tables: 
| Service | Est. Cost |
|---|---|
| GCS storage + ops | ~$0.09 |
| BigQuery storage + queries | ~$0.04 |
| Airflow (local Astro CLI) | Free |
| **Total** | **~$0.13/month** |
