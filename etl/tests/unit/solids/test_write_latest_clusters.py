from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.resources.boto_client import mock_boto_client
from etl.resources.database_client import mock_database_client
from etl.solids.write_latest_clusters import get_latest_clusters, prep_latest_clusters, write_to_bucket
from ptbmodels.models import Article, ArticleCluster, ArticleClusterKeyword, Source


sid1 = uuid4()
sid2 = uuid4()

fake_articles = [
    Article(**{"id": uuid4(),
               "url": "https://fake.com",
               "source_id": sid1,
               "source": Source(**{"id": sid1, "name": "source1"}),
               "title": "fake title",
               "published_at": datetime.now(tz=timezone.utc)}),
    Article(**{"id": uuid4(),
               "url": "https://notreal.com",
               "source_id": sid2,
               "source": Source(**{"id": sid2, "name": "source2"}),
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
        "added_at": datetime.now(tz=timezone.utc),
        "articles": fake_articles,
        "keywords": fake_topics
    }), 5),
    (ArticleCluster(**{
        "id": uuid4(),
        "type": "PTB0",
        "parameters": {"threshold": 0.4},
        "begin": datetime.now(tz=timezone.utc) - timedelta(days=1),
        "end": datetime.now(tz=timezone.utc),
        "added_at": datetime.now(tz=timezone.utc),
        "articles": fake_articles,
        "keywords": fake_topics
    }), 4),
    (ArticleCluster(**{
        "id": uuid4(),
        "type": "PTB0",
        "parameters": {"threshold": 0.4},
        "begin": datetime.now(tz=timezone.utc) - timedelta(days=1),
        "end": datetime.now(tz=timezone.utc),
        "added_at": datetime.now(tz=timezone.utc),
        "articles": fake_articles,
        "keywords": fake_topics
    }), 3)
]


def test_get_latest_clusters():
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
    expected_prepped = {
        "added_at": expected_clusters[0][0].added_at,
        "clusters": [
            {
                "topics": [{"term": k.term, "weight": k.weight} for k in c[0].keywords],
                "articles": [{"title": a.title, "url": a.url, "source": a.source.name,
                              "date": a.published_at.strftime("%d-%m-%Y")} for a in c[0].articles],
                "source_count": c[1]
            }
            for c in expected_clusters
        ]
    }

    result: SolidExecutionResult = execute_solid(
        prep_latest_clusters,
        input_values={"clusters": expected_clusters}
    )

    assert result.success
    assert result.output_value() == expected_prepped


def test_write_to_bucket():
    boto_client = mock_boto_client()

    def _test_boto_client(_init_context):
        return boto_client

    result: SolidExecutionResult = execute_solid(
        write_to_bucket,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"boto_client": ResourceDefinition(_test_boto_client)}),
        input_values={"prepped_data": {"fake": "data"}},
        run_config={"solids": {
            "write_to_bucket": {"config": {"bucket": "my-bucket", "key": "my-file.json"}}
        }}
    )

    assert result.success
    assert boto_client.put_object.called_once()
