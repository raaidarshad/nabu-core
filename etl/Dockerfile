FROM python:3.9.5-slim

RUN pip install poetry

RUN apt-get update
RUN apt-get -y install libpq-dev gcc

COPY . /app/

WORKDIR /app

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-dev
RUN python -m spacy download en_core_web_lg
