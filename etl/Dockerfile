FROM python:3.9.1-slim

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

# ==> Add user code layer
COPY ./ /
