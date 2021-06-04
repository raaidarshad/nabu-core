from dataclasses import dataclass

from uuid import UUID, uuid4
from unittest.mock import MagicMock, Mock

from dagster import configured, resource
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@resource(config_schema={"connection_string": str})
def database_client(init_context) -> Session:
    engine = create_engine(init_context.resource_config["connection_string"])
    db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return db_session()


@configured(configurable=database_client)
def local_database_client(_init_context):
    return {"connection_string": "postgresql://postgres:postgres@localhost:5432/postgres"}


@resource
def test_database_client(_init_context) -> Session:
    return MagicMock(Session)
