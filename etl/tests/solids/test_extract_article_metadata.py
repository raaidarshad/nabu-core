from datetime import timedelta
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.common import get_source_names, get_current_time
from etl.resources.database_client import mock_database_client
from etl.solids.extract_article_metadata import get_sources, load_articles
from ptbmodels.models import Article, Source


def test_get_sources():
    source_names = get_source_names()[:3]
    expected_sources = [Source(id=idx, name=n) for idx, n in enumerate(source_names)]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_sources)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_sources,
        mode_def=ModeDefinition(name="test_get_all_sources",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        run_config={
            "solids": {
                "get_sources": {
                    "config": {
                        "sources": source_names
                    }
                }
            }
        }
    )

    assert result.success
    assert result.output_value() == expected_sources


def test_get_rss_feeds():
    ...


def test_get_raw_feeds():
    ...


def test_get_new_raw_feed_entries():
    ...


def test_transform_raw_feed_entries_to_articles():
    ...


def test_load_articles():
    articles = [
        Article(id=uuid4(),
                url="https://fake.com",
                source_id=0,
                summary="summary",
                title="title",
                published_at=get_current_time() - timedelta(hours=1),
                added_at=get_current_time())
    ]

    db_mock = mock_database_client()

    def _test_db_client(_init_context):
        db_mock.exec = Mock(return_value=1)
        db_mock.commit = Mock(return_value=1)
        a = Mock()
        a.count = Mock(return_value=1)
        db_mock.query = Mock(return_value=a)
        return db_mock

    result: SolidExecutionResult = execute_solid(
        load_articles,
        # needs a database_client that has add_all and commit methods
        mode_def=ModeDefinition(name="test_load_articles",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        input_values={"articles": articles}
    )

    assert result.success
    assert result.output_value() == articles
    # count of rows in mock should be the same, therefore no asset should be materialized
    assert result.materializations_during_compute == []
    assert db_mock.exec.called_once()
    assert db_mock.commit.called_once()
