FROM python:3.9.5-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get -y install libpq-dev gcc && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

COPY . /etl/

WORKDIR /etl

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-dev --no-root \
    && python -m spacy download en_core_web_lg
