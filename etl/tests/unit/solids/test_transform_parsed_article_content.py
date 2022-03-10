from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import mock_database_client
from etl.resources.html_parser import html_parser
from etl.solids.transform_parsed_article_content import get_raw_content, parse_raw_content, load_parsed_content
from ptbmodels.models import Article, ParsedContent, RawContent, RssFeed


def test_get_raw_content():
    expected_raw_content = [
        RawContent(article_id=uuid4(),
                   content=f"fake{idx}",
                   added_at=get_current_time()
                   ) for idx in range(3)
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_raw_content)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
    )

    assert result.success
    assert result.output_value() == expected_raw_content


def test_parse_raw_content():
    added_at = get_current_time()
    rss_feed = RssFeed(
        id=uuid4(),
        source_id=0,
        url="https://fake.com/feed",
        parser_config={"id": "my-id"}
    )

    article = Article(
        id=uuid4(),
        source_id=0,
        rss_feed_id=rss_feed.id,
        url="https://fake.com/article-link",
        summary="summary",
        title="title",
        published_at=get_current_time(),
        rss_feed=rss_feed
    )

    content1 = "fake joined"
    content2 = "text"

    raw_content = RawContent(article_id=article.id,
                             content=f"<div id='my-id'><p>{content1}</p><p>{content2}</p></div><div><p>hi</p></div>",
                             added_at=get_current_time(),
                             article=article
                             )

    expected_parsed_content = ParsedContent(article_id=article.id,
                                            content=" ".join([content1, content2]),
                                            added_at=added_at)

    result: SolidExecutionResult = execute_solid(
        parse_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"html_parser": html_parser}),
        input_values={"raw_content": [raw_content]},
        run_config={"solids": {"parse_raw_content": {"config": {"runtime": datetime_to_str(added_at)}}}}
    )

    assert result.success
    assert result.output_value() == [expected_parsed_content]


def test_parse_raw_content_regex():
    added_at = get_current_time()
    rss_feed = RssFeed(
        id=uuid4(),
        source_id=0,
        url="https://fake.com/feed",
        parser_config={"class_": "MyClass", "regex": True}
    )

    article = Article(
        id=uuid4(),
        source_id=0,
        rss_feed_id=rss_feed.id,
        url="https://fake.com/article-link",
        summary="summary",
        title="title",
        published_at=get_current_time(),
        rss_feed=rss_feed
    )

    content1 = "oh na na"
    content2 = "what's my name"

    raw_content = RawContent(article_id=article.id,
                             content=f"<div class='MyClass'><p>{content1}</p><p>{content2}</p></div><div><p>merp</p></div>",
                             added_at=get_current_time(),
                             article=article
                             )

    expected_parsed_content = ParsedContent(article_id=article.id,
                                            content=" ".join([content1, content2]),
                                            added_at=added_at)

    result: SolidExecutionResult = execute_solid(
        parse_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"html_parser": html_parser}),
        input_values={"raw_content": [raw_content]},
        run_config={"solids": {"parse_raw_content": {"config": {"runtime": datetime_to_str(added_at)}}}}
    )

    assert result.success
    assert result.output_value() == [expected_parsed_content]


def test_parse_raw_content_list_config():
    added_at = get_current_time()
    rss_feed = RssFeed(
        id=uuid4(),
        source_id=0,
        url="https://fake.com/feed",
        parser_config=[{"class_": "MyClass", "regex": True}, {"class_": "article-body", "regex": True}]
    )

    article = Article(
        id=uuid4(),
        source_id=0,
        rss_feed_id=rss_feed.id,
        url="https://fake.com/article-link",
        summary="summary",
        title="title",
        published_at=get_current_time(),
        rss_feed=rss_feed
    )

    content1 = "oh na na"
    content2 = "what's my name"

    raw_content = RawContent(article_id=article.id,
                             content=f"<div class='article-body'><p>{content1}</p><p>{content2}</p></div><div><p>merp</p></div>",
                             added_at=get_current_time(),
                             article=article
                             )

    expected_parsed_content = ParsedContent(article_id=article.id,
                                            content=" ".join([content1, content2]),
                                            added_at=added_at)

    result: SolidExecutionResult = execute_solid(
        parse_raw_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"html_parser": html_parser}),
        input_values={"raw_content": [raw_content]},
        run_config={"solids": {"parse_raw_content": {"config": {"runtime": datetime_to_str(added_at)}}}}
    )

    assert result.success
    assert result.output_value() == [expected_parsed_content]


def test_load_parsed_content():
    parsed_content = [
        ParsedContent(
            article_id=uuid4(),
            content=f"rawcontent{idx}",
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
        load_parsed_content,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        input_values={"entities": parsed_content}
    )

    assert result.success
    assert result.output_value() == parsed_content
    # count of rows in mock should be the same, therefore no asset should be materialized
    assert result.materializations_during_compute == []
    assert db.exec.called_once()
    assert db.commit.called_once()
