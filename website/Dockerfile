FROM python:3.9.5-slim as req
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry && poetry export -o requirements.txt

FROM python:3.9.5-slim as builder
RUN apt-get update && apt-get install -y libpq-dev gcc
COPY --from=req requirements.txt .
RUN pip install --user -r requirements.txt

FROM nikolaik/python-nodejs:python3.9-nodejs16-slim as runner

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev
COPY --from=builder /root/.local /root/.local
COPY . /app/
WORKDIR /app
RUN npm install && npm run build
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
