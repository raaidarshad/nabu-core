# build client-side code
FROM nikolaik/python-nodejs:python3.9-nodejs16

COPY . /app/

WORKDIR /app

RUN npm install

RUN npm run build

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-dev

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
