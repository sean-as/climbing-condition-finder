.PHONY: airflow-up airflow-down airflow-logs dbt-run dbt-test dbt-build ui install

# --- Airflow (docker-compose, run from repo root) ---
airflow-up:
	docker compose up -d

airflow-down:
	docker compose down

airflow-logs:
	docker compose logs -f

# --- dbt (run from airflow/dbt/climbing_weather) ---
dbt-run:
	cd airflow/dbt/climbing_weather && DBT_PROFILES_DIR=$(CURDIR)/.dbt poetry run dbt run

dbt-test:
	cd airflow/dbt/climbing_weather && DBT_PROFILES_DIR=$(CURDIR)/.dbt poetry run dbt test

dbt-build:
	cd airflow/dbt/climbing_weather && DBT_PROFILES_DIR=$(CURDIR)/.dbt poetry run dbt build

# --- UI (run from ui/) ---
ui:
	cd ui && poetry run uvicorn app.main:app --reload --port 8000

# --- deps ---
install:
	poetry install
