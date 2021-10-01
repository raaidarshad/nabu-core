from unittest.mock import Mock

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.common import get_source_names
from etl.resources.database_client import mock_database_client
from etl.solids.extract_article_metadata import get_sources
from ptbmodels.models import Source


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
    ...

