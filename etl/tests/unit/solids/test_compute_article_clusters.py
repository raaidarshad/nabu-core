from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import mock_database_client
from etl.solids.compute_article_clusters import get_term_counts
from ptbmodels.models import TermCount, ArticleCluster


def test_get_term_counts():
    expected_term_counts = [
        TermCount(article_id=uuid4(),
                  term=f"term{idx}",
                  count=idx,
                  added_at=get_current_time()
                  ) for idx in range(3)
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_term_counts)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_term_counts,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)})
    )

    assert result.success
    assert result.output_value() == expected_term_counts



def test_compute_tfidf():
    ...


def test_compute_article_clusters():
    ...


def test_load_article_clusters():
    ...
