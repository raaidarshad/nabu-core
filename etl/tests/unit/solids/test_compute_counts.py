from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import mock_database_client
from etl.solids.compute_counts import get_parsed_content, compute_term_counts, load_term_counts
from ptbmodels.models import ParsedContent, TermCount


def test_get_parsed_content():
    expected_parsed_content = [
        ParsedContent(article_id=uuid4(),
                      content=f"fake{idx}",
                      added_at=get_current_time()
                      ) for idx in range(3)
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_parsed_content)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_parsed_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
    )

    assert result.success
    assert result.output_value() == expected_parsed_content


def test_compute_term_counts():
    now = get_current_time()
    article_id1 = uuid4()
    article_id2 = uuid4()
    parsed_content = [
        ParsedContent(
            article_id=article_id1,
            content="fake fake content",
            added_at=now
        ),
        ParsedContent(
            article_id=article_id2,
            content="fake content raaid",
            added_at=now
        )
    ]

    expected_term_counts = [
        TermCount(
            article_id=article_id1,
            term="fake",
            count=2,
            added_at=now
        ),
        TermCount(
            article_id=article_id1,
            term="content",
            count=1,
            added_at=now
        ),
        TermCount(
            article_id=article_id2,
            term="fake",
            count=1,
            added_at=now
        ),
        TermCount(
            article_id=article_id2,
            term="content",
            count=1,
            added_at=now
        ),
        TermCount(
            article_id=article_id2,
            term="raaid",
            count=1,
            added_at=now
        )
    ]

    result: SolidExecutionResult = execute_solid(
        compute_term_counts,
        run_config={"solids": {"compute_term_counts": {"config": {"runtime": datetime_to_str(now)}}}},
        input_values={"parsed_content": parsed_content}
    )

    assert result.success
    assert result.output_value() == expected_term_counts


def test_load_term_counts():
    term_counts = [
        TermCount(
            article_id=uuid4(),
            term=f"term{idx}",
            count=idx,
            added_at=get_current_time()
        ) for idx in range(3)
    ]

    db = mock_database_client()

    def _test_db_client(_init_context):
        db.exec = Mock(return_value=1)
        db.commit = Mock(return_value=1)
        a = Mock()
        a.count = Mock(return_value=1)
        db.query = Mock(return_value=a)
        return db

    result: SolidExecutionResult = execute_solid(
        load_term_counts,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        input_values={"entities": term_counts}
    )

    assert result.success
    assert result.output_value() == term_counts
    # count of rows in mock should be the same, therefore no asset should be materialized
    assert result.materializations_during_compute == []
    assert db.exec.called_once()
    assert db.commit.called_once()
