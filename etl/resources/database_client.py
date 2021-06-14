from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock
from uuid import uuid4

from dagster import configured, resource
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from etl.db.models import Article as DbArticle


@resource(config_schema={"connection_string": str})
def database_client(init_context) -> Session:
    engine = create_engine(init_context.resource_config["connection_string"])
    db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return db_session()


@configured(configurable=database_client)
def local_database_client(_init_context):
    return {"connection_string": "postgresql://postgres:postgres@localhost:5432/postgres"}


@resource
def mock_database_client(_init_context) -> Session:
    return MagicMock(Session)


@resource
def compute_counts_test_database_client(_init_context):
    fake_articles = [
        DbArticle(**{"id": uuid4(),
                     "url": "https://fake.com",
                     "source_id": uuid4(),
                     "title": "fake title",
                     "published_at": datetime.now(tz=timezone.utc),
                     "parsed_content": "fake raaid content"}),
        DbArticle(**{"id": uuid4(),
                     "url": "https://notreal.com",
                     "source_id": uuid4(),
                     "title": "unreal title",
                     "published_at": datetime.now(tz=timezone.utc) - timedelta(seconds=30),
                     "parsed_content": "unreal raaid content"})
    ]
    db = mock_database_client()
    a = Mock()
    b = Mock()
    c = Mock()
    d = Mock()
    d.all = Mock(return_value=fake_articles)
    c.filter = Mock(return_value=d)
    b.outerjoin = Mock(return_value=c)
    a.filter = Mock(return_value=b)
    db.query = Mock(return_value=a)

    db.add_all = Mock(return_value=1)
    db.commit = Mock(return_value=1)

    return db
