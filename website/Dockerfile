# build client-side code
FROM node:14.15.4 as client

RUN npm install

RUN npm build

# ==> Add user code layer, including newly generated static assets
COPY ./ /

# python server
FROM python:3.9.1-slim as server

RUN pip install poetry

RUN apt-get update -yqq

COPY pyproject.toml /

RUN poetry config virtualenvs.create false \
     && poetry install --no-interaction --no-ansi --no-dev

# Cleanup
RUN  rm -rf /var \
    &&  rm -rf /root/.cache  \
    &&  rm -rf /usr/lib/python2.7 \
    &&  rm -rf /usr/lib/x86_64-linux-gnu/guile

RUN uvicorn app:app --reload

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
