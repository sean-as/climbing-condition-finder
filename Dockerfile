FROM apache/airflow:2.11.2

RUN pip install --no-cache-dir poetry==2.4.1

WORKDIR /opt/airflow
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
 && poetry install --no-root