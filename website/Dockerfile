FROM nikolaik/python-nodejs:python3.9-nodejs16-slim

COPY . /app/

WORKDIR /app

RUN npm install && npm run build

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-dev --no-root

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
