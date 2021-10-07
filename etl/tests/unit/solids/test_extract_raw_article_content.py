from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, build_init_resource_context, execute_solid
from requests.exceptions import HTTPError

from etl.common import datetime_to_str
from etl.resources.database_client import mock_database_client
from etl.resources.http_client import mock_http_client
from etl.resources.thread_local import mock_thread_local
from etl.solids.extract_raw_article_content import get_articles, request_raw_content, load_raw_content
from ptbmodels.models import Article, RawContent


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
    added_at = datetime.now(tz=timezone.utc)
    article_with_good_url = Article(id=uuid4(),
                                    url=f"https://fake.com",
                                    source_id=0,
                                    title=f"title",
                                    published_at=datetime.now(tz=timezone.utc),
                                    summary=f"summary",
                                    added_at=added_at
                                    )
    expected_raw_content = RawContent(
        article_id=article_with_good_url.id,
        content="text",
        added_at=added_at
    )

    article_with_bad_url = Article(id=uuid4(),
                                   url=f"htt//malformed^^$)",
                                   source_id=0,
                                   title=f"titlebad",
                                   published_at=datetime.now(tz=timezone.utc),
                                   summary=f"summaryohno",
                                   added_at=datetime.now(tz=timezone.utc)
                                   )

    def _test_good_client(_init_context):
        with build_init_resource_context(resources={"thread_local": mock_thread_local}) as c:
            client = mock_http_client(c)
            response = Mock()
            response.status_code = 200
            response.text = "text"
            client.get = Mock(return_value=response)
            return client

    result: SolidExecutionResult = execute_solid(
        request_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"http_client": ResourceDefinition(_test_good_client)}),
        input_values={"articles": [article_with_good_url]},
        run_config={"solids": {"request_raw_content": {"config": {"runtime": datetime_to_str(added_at)}}}}
    )

    assert result.success
    assert result.output_value() == [expected_raw_content]


def test_request_raw_content_non_200():
    added_at = datetime.now(tz=timezone.utc)

    article_with_bad_url = Article(id=uuid4(),
                                   url="https://faketyfakefake.fake",
                                   source_id=0,
                                   title="titlebad",
                                   published_at=datetime.now(tz=timezone.utc),
                                   summary="summaryohno",
                                   added_at=datetime.now(tz=timezone.utc)
                                   )

    def _test_good_client(_init_context):
        with build_init_resource_context(resources={"thread_local": mock_thread_local}) as c:
            client = mock_http_client(c)
            response = Mock()
            response.status_code = 404
            client.get = Mock(return_value=response)
            return client

    result: SolidExecutionResult = execute_solid(
        request_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"http_client": ResourceDefinition(_test_good_client)}),
        input_values={"articles": [article_with_bad_url]},
        run_config={"solids": {"request_raw_content": {"config": {"runtime": datetime_to_str(added_at)}}}}
    )

    assert result.success
    assert result.output_value() == []


def test_request_raw_content_http_error():
    added_at = datetime.now(tz=timezone.utc)

    article_with_bad_url = Article(id=uuid4(),
                                   url="https://faketyfakefake.fake",
                                   source_id=0,
                                   title="titlebad",
                                   published_at=datetime.now(tz=timezone.utc),
                                   summary="summaryohno",
                                   added_at=datetime.now(tz=timezone.utc)
                                   )

    def _test_good_client(_init_context):
        with build_init_resource_context(resources={"thread_local": mock_thread_local}) as c:
            client = mock_http_client(c)
            client.get = Mock(side_effect=HTTPError("Ohno"))
            return client

    result: SolidExecutionResult = execute_solid(
        request_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"http_client": ResourceDefinition(_test_good_client)}),
        input_values={"articles": [article_with_bad_url]},
        run_config={"solids": {"request_raw_content": {"config": {"runtime": datetime_to_str(added_at)}}}}
    )

    assert result.success
    assert result.output_value() == []


def test_load_raw_content():
    ...
