from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.db.models import Article as DbArticle
from etl.models import Article
from etl.resources.database_client import mock_database_client
from etl.solids.compute_counts import get_articles, compute_count_matrix, compose_rows, load_counts


def test_get_articles():
    fake_articles = [
        DbArticle(**{"id": uuid4(),
                     "url": "https://fake.com",
                     "source_id": uuid4(),
                     "title": "fake title",
                     "published_at": datetime.now(tz=timezone.utc),
                     "parsed_content": "fake parsed content"}),
        DbArticle(**{"id": uuid4(),
                     "url": "https://notreal.com",
                     "source_id": uuid4(),
                     "title": "unreal title",
                     "published_at": datetime.now(tz=timezone.utc) - timedelta(seconds=30),
                     "parsed_content": "moar parsed content"})
    ]

    def _test_db_client(_init_context):
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
        return db

    result: SolidExecutionResult = execute_solid(
        get_articles,
        mode_def=ModeDefinition(name="test_get_articles",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        run_config={
            "solids": {
                "get_articles": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc) - timedelta(hours=1))
                    }
                }
            }
        }
    )

    assert result.success
    assert len(result.output_value()) == len(fake_articles)
    for idx, article in enumerate(result.output_value()):
        assert Article(**fake_articles[idx].__dict__) == article


def test_compute_count_matrix():
    pass


def test_compose_rows():
    pass


def test_load_counts():
    pass
