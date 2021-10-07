from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.resources.database_client import mock_database_client
from etl.solids.extract_raw_article_content import get_articles, request_raw_content, load_raw_content
from ptbmodels.models import Article


def test_get_articles():
    expected_articles = [
        Article(id=uuid4(),
                url=f"https://fake{idx}.com",
                source_id=idx,
                title=f"title{idx}",
                published_at=datetime.now(tz=timezone.utc),
                summary=f"summary{idx}",
                added_at=datetime.now(tz=timezone.utc)
                ) for idx in range(3)
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_articles)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_articles,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
    )

    assert result.success
    assert result.output_value() == expected_articles


def test_request_raw_content():
    ...


def test_load_raw_content():
    ...