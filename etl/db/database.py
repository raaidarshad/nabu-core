import os
from urllib import parse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

# default postgres driver is psycopg2 https://docs.sqlalchemy.org/en/14/core/engines.html#postgresql
#  form for postgres should look like "postgresql://user:password@postgresserver/db", need to ensure escapes on password
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername=os.getenv("DB_DRIVER"),
    username=os.getenv("DB_USERNAME"),
    password=parse.quote_plus(os.getenv("DB_PASSWORD")),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"))

engine = create_engine(SQLALCHEMY_DATABASE_URL)
DbSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
