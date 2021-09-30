from datetime import datetime, timedelta, timezone
import os
from unittest.mock import MagicMock, Mock
from uuid import uuid4

from dagster import configured, resource
from sqlalchemy.future.engine import Engine
from sqlmodel import Session, create_engine

from ptbmodels.models import Article, Source, TermCount


@resource(config_schema={"connection_string": str})
def database_engine(init_context) -> Engine:
    return create_engine(init_context.resource_config["connection_string"])


@configured(database_engine)
def local_database_engine(init_context):
    return {"connection_string": "postgresql://postgres:postgres@localhost:5432/postgres"}


@configured(database_engine)
def cloud_database_engine(init_context):
    return {"connection_string": os.getenv("DB_CONNECTION_STRING")}


@resource
def mock_database_engine() -> Engine:
    return MagicMock(Engine)


@resource(config_schema={"connection_string": str})
def database_client(init_context) -> Session:
    engine = create_engine(init_context.resource_config["connection_string"])
    db_session = Session(autocommit=False, autoflush=False, bind=engine)
    return db_session


@configured(database_client)
def local_database_client(init_context):
    return {"connection_string": "postgresql://postgres:postgres@localhost:5432/postgres"}


@configured(database_client)
def cloud_database_client(init_context):
    return {"connection_string": os.getenv("DB_CONNECTION_STRING")}


@resource
def mock_database_client() -> Session:
    return MagicMock(Session)


@resource
def extract_articles_test_database_client():
    fake_sources = [
        Source(**{"id": uuid4(),
                  "name": "name",
                  "rss_url": "https://fake.com",
                  "html_parser_config": {"id": "merp"}
                  }),
        Source(**{"id": uuid4(),
                  "name": "nametwo",
                  "rss_url": "https://unreal.com",
                  "html_parser_config": {"id": "flerp"}
                  })
    ]
    db = mock_database_client()
    t_query = Mock()
    t_query.all = Mock(return_value=fake_sources)
    t_query.count = Mock(return_value=1)
    db.query = Mock(return_value=t_query)

    db.add_all = Mock(return_value=1)
    db.commit = Mock(return_value=1)

    return db


@resource
def compute_counts_test_database_client():
    fake_articles = [
        Article(**{"id": uuid4(),
                   "url": "https://fake.com",
                   "source_id": uuid4(),
                   "title": "fake title",
                   "published_at": datetime.now(tz=timezone.utc),
                   "parsed_content": "fake raaid content"}),
        Article(**{"id": uuid4(),
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
    a.count = Mock(return_value=1)
    a.filter = Mock(return_value=b)
    db.query = Mock(return_value=a)

    db.add_all = Mock(return_value=1)
    db.commit = Mock(return_value=1)

    return db


@resource
def compute_clusters_test_database_client():
    # and need to load clusters
    fake_articles = [
        Article(**{"id": uuid4(),
                   "url": "https://fake.com",
                   "source_id": uuid4(),
                   "title": "fake title",
                   "published_at": datetime.now(tz=timezone.utc),
                   "parsed_content": "fake raaid content"}),
        Article(**{"id": uuid4(),
                   "url": "https://notreal.com",
                   "source_id": uuid4(),
                   "title": "unreal title",
                   "published_at": datetime.now(tz=timezone.utc) - timedelta(seconds=30),
                   "parsed_content": "unreal raaid content"})
    ]

    fake_counts = [
        TermCount(article_id=uuid4(), term="fake", count=2),
        TermCount(article_id=uuid4(), term="news", count=3),
    ]

    db = mock_database_client()
    a = Mock()
    b = Mock()

    b.all = Mock(return_value=fake_articles)
    a.filter = Mock(return_value=b)
    db.query = Mock(return_value=a)

    c = Mock()
    d = Mock()

    d.all = Mock(return_value=fake_counts)
    c.filter = Mock(return_value=d)
    a.join = Mock(return_value=c)

    db.add_all = Mock(return_value=1)
    db.commit = Mock(return_value=1)

    return db
