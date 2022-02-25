FROM python:3.9.5-slim as req
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry && poetry export -o requirements.txt

FROM python:3.9.5-slim as builder
RUN apt-get update && apt-get install -y libpq-dev gcc
COPY --from=req requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9.5-slim as runner
RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev
COPY --from=builder /root/.local /root/.local
COPY . /api/
ENV PATH=/root/.local/bin:$PATH
CMD cd api/api && gunicorn --workers 8 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 main:app
