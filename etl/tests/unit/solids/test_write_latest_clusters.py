from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.resources.database_client import mock_database_client
from etl.solids.write_latest_clusters import get_latest_clusters
from ptbmodels.models import Article, ArticleCluster, ArticleClusterKeyword


def test_get_latest_clusters():
    fake_articles = [
        Article(**{"id": uuid4(),
                   "url": "https://fake.com",
                   "source_id": uuid4(),
                   "title": "fake title",
                   "published_at": datetime.now(tz=timezone.utc)}),
        Article(**{"id": uuid4(),
                   "url": "https://notreal.com",
                   "source_id": uuid4(),
                   "title": "unreal title",
                   "published_at": datetime.now(tz=timezone.utc) - timedelta(seconds=30)})
    ]

    fake_topics = [
        ArticleClusterKeyword(**{
            "article_cluster_id": uuid4(),
            "term": "morp",
            "weight": 0.7
        }),
        ArticleClusterKeyword(**{
            "article_cluster_id": uuid4(),
            "term": "florp",
            "weight": 0.6
        })
    ]

    expected_clusters = [
        (ArticleCluster(**{
            "id": uuid4(),
            "type": "PTB0",
            "parameters": {"threshold": 0.4},
            "begin": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "end": datetime.now(tz=timezone.utc),
            "articles": fake_articles,
            "keywords": fake_topics
        }), 5),
        (ArticleCluster(**{
            "id": uuid4(),
            "type": "PTB0",
            "parameters": {"threshold": 0.4},
            "begin": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "end": datetime.now(tz=timezone.utc),
            "articles": fake_articles,
            "keywords": fake_topics
        }), 4),
        (ArticleCluster(**{
            "id": uuid4(),
            "type": "PTB0",
            "parameters": {"threshold": 0.4},
            "begin": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "end": datetime.now(tz=timezone.utc),
            "articles": fake_articles,
            "keywords": fake_topics
        }), 3)
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()

        a = Mock()

        a.all = Mock(return_value=expected_clusters)
        db.exec = Mock(return_value=a)

        return db

    result: SolidExecutionResult = execute_solid(
        get_latest_clusters,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)})
    )

    assert result.success
    assert result.output_value() == expected_clusters


def test_prep_latest_clusters():
    ...


def test_write_to_bucket():
    ...
