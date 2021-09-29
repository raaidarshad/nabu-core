from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from unittest.mock import Mock

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid
import feedparser

from etl.pipelines.extract_articles import test_mode
from etl.resources.database_client import mock_database_client
from etl.resources.html_parser import mock_html_parser
from etl.resources.http_client import mock_http_client
from etl.resources.thread_local import mock_thread_local
from etl.resources.rss_parser import mock_rss_parser
from etl.solids.extract_articles import get_all_sources, create_source_map, get_latest_feeds, filter_to_new_entries, \
    extract_articles_solid, load_articles
from ptbmodels.models import Article, Feed, FeedEntry, Source


sources = [
    Source(id=uuid4(), name="source1", rss_url="https://fakeone.com/", html_parser_config={"id": "merp"}),
    Source(id=uuid4(), name="source2", rss_url="https://faketwo.com/", html_parser_config={"id": "merp"})
]


def test_get_all_sources():
    fake_sources = [
        Source(**{"id": uuid4(),
                  "name": "name",
                  "rss_url": "https://fake.com",
                  "html_parser_config": {"id": "merp"}
                  })
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=fake_sources)
        db.query = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_all_sources,
        # needs a database_client that returns a list of Source-like objects when db.query().all() is called
        mode_def=ModeDefinition(name="test_get_all_sources",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)})
    )

    assert result.success
    assert len(result.output_value()) == len(fake_sources)
    test_source = result.output_value()[0]
    assert isinstance(test_source, Source)
    assert test_source.name == "name"
    assert test_source.rss_url == "https://fake.com"
    assert test_source.html_parser_config == {"id": "merp"}
    assert isinstance(test_source.id, UUID)


def test_create_source_map():
    result: SolidExecutionResult = execute_solid(
        create_source_map,
        mode_def=test_mode,
        input_values={"sources": sources}
    )

    assert result.success
    assert len(result.output_value()) == len(sources)
    for i, (k, v) in enumerate(result.output_value().items()):
        assert k == sources[i].id
        assert v == sources[i]


def test_get_latest_feeds():
    parsed = feedparser.FeedParserDict({
        "status": 200,
        "feed": feedparser.FeedParserDict(
            {"updated": str(datetime.now(timezone.utc)),
             "link": "https://www.fake.com",
             "title": "myfeed_title",
             "subtitle": "myfeed_subtitle"
             }),
        "entries": [feedparser.FeedParserDict(
            {"title": "fake_title",
             "summary": "fake_summary",
             "published": str(datetime.now(timezone.utc)),
             "link": "https://www.fake.com",
             "author": "pencil mcpen"
             })]
    })

    def _test_rss_parser(_init_context):
        rss_mock = mock_rss_parser()
        rss_mock.parse = Mock(return_value=parsed)
        return rss_mock

    result: SolidExecutionResult = execute_solid(
        get_latest_feeds,
        mode_def=ModeDefinition(name="test_get_latest_feeds",
                                resource_defs={"rss_parser": ResourceDefinition(_test_rss_parser)}),
        input_values={"sources": sources},
        run_config={
            "solids": {
                "get_latest_feeds": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc))
                    }
                }
            }
        }
    )

    assert result.success
    assert len(result.output_value()) == len(sources)
    for idx, output in enumerate(result.output_value()):
        assert isinstance(output, Feed)
        assert output == Feed(title=parsed.feed.title,
                              subtitle=parsed.feed.subtitle,
                              entries=[
                                  FeedEntry(
                                      title=parsed.entries[0].title,
                                      summary=parsed.entries[0].summary,
                                      published_at=parsed.entries[0].published,
                                      link=parsed.entries[0].link,
                                      author=parsed.entries[0].author,
                                      source_id=sources[idx].id
                                  )
                              ],
                              link=parsed.feed.link,
                              updated_at=parsed.feed.updated,
                              source_id=sources[idx].id)


def test_filter_to_new_entries():
    sid = uuid4()
    entries = [FeedEntry(title="entry1",
                         summary="summary",
                         published_at=datetime.now(timezone.utc),
                         link="https://fake.com",
                         author="pencil mcpen",
                         source_id=sid),
               FeedEntry(title="entry2",
                         summary="summary2",
                         published_at=datetime.now(timezone.utc) - timedelta(minutes=2),
                         link="https://fake.com",
                         author="pencil mcpen",
                         source_id=sid)
               ]

    result: SolidExecutionResult = execute_solid(
        filter_to_new_entries,
        mode_def=ModeDefinition(name="test_filter_to_new_entries"),
        input_values={
            "feeds": [
                Feed(title="feed1",
                     entries=entries,
                     link="https://fake.com",
                     updated_at=datetime.now(timezone.utc),
                     source_id=sid)
            ]},
        run_config={
            "solids": {
                "filter_to_new_entries": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc) - timedelta(seconds=30))
                    }
                }
            }
        }
    )

    assert result.success
    # make sure the new entry is present and the old (before the filter threshold) is absent
    assert result.output_value() == [entries[0]]


def test_extract_articles():
    sid = uuid4()
    entries = [
        FeedEntry(title="entry1",
                  summary="summary",
                  published_at=datetime.now(timezone.utc),
                  link="https://fake.com",
                  author="pencil mcpen",
                  source_id=sid)
    ]
    source_map = {
        sid: Source(id=uuid4(),
                    name="source1",
                    rss_url="https://fakeone.com/",
                    html_parser_config={"id": "merp"})}

    parsed_text = "my fake test text"

    def _test_html_parser(_init_context):
        mock_parser = mock_html_parser()
        mock_parser.extract = Mock(return_value=parsed_text)
        return mock_parser

    result: SolidExecutionResult = execute_solid(
        extract_articles_solid,
        mode_def=ModeDefinition(name="test_extract_articles",
                                resource_defs={"html_parser": ResourceDefinition(_test_html_parser),
                                               "http_client": mock_http_client,
                                               "thread_local": mock_thread_local}),
        input_values={"entries": entries, "source_map": source_map}
    )

    assert result.success
    for idx, entry in enumerate(entries):
        # need to go field by field because UUID of article will be generated
        expected = Article(parsed_content=parsed_text, **entry.dict())
        actual = result.output_value()[idx]

        assert expected.title == actual.title
        assert expected.summary == actual.summary
        assert expected.source_id == actual.source_id
        assert expected.url == actual.url
        assert expected.published_at == actual.published_at
        assert expected.authors == actual.authors
        assert expected.parsed_content == actual.parsed_content


def test_extract_articles_parse_fails():
    sid = uuid4()
    entries = [
        FeedEntry(title="entry1",
                  summary="summary",
                  published_at=datetime.now(timezone.utc),
                  link="https://fake.com",
                  author="pencil mcpen",
                  source_id=sid)
    ]
    source_map = {
        sid: Source(id=uuid4(),
                    name="source1",
                    rss_url="https://fakeone.com/",
                    html_parser_config={"id": "merp"})}

    parsed_text = "my fake test text"

    def _test_html_parser(_init_context):
        mock_parser = mock_html_parser()
        mock_parser.extract = Mock(side_effect=ValueError("ohno"))
        return mock_parser

    result: SolidExecutionResult = execute_solid(
        extract_articles_solid,
        mode_def=ModeDefinition(name="test_extract_articles",
                                resource_defs={"html_parser": ResourceDefinition(_test_html_parser),
                                               "http_client": mock_http_client,
                                               "thread_local": mock_thread_local}),
        input_values={"entries": entries, "source_map": source_map}
    )

    assert result.success
    for idx, entry in enumerate(entries):
        # need to go field by field because UUID of article will be generated
        expected = Article(parsed_content=parsed_text, **entry.dict())
        actual = result.output_value()[idx]

        assert expected.title == actual.title
        assert expected.summary == actual.summary
        assert expected.source_id == actual.source_id
        assert expected.url == actual.url
        assert expected.published_at == actual.published_at
        assert expected.authors == actual.authors
        # this is intentional, it should NOT be the parsed content here and should default to summary
        assert expected.summary == actual.parsed_content


def test_load_articles():
    articles = [
        Article(id=uuid4(),
                url="https://fake.com",
                source_id=uuid4(),
                title="title",
                published_at=datetime.now(timezone.utc))
    ]

    db_articles = [Article(**article.dict()) for article in articles]

    db_mock = mock_database_client()

    def _test_db_client(_init_context):
        db_mock.exec = Mock(return_value=1)
        db_mock.commit = Mock(return_value=1)
        return db_mock

    result: SolidExecutionResult = execute_solid(
        load_articles,
        run_config={
            "solids": {
                "load_articles": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc) - timedelta(seconds=30))
                    }
                }
            }
        },
        # needs a database_client that has add_all and commit methods
        mode_def=ModeDefinition(name="test_load_articles",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        input_values={"articles": articles}
    )

    assert result.success
    assert db_mock.add_all.exec(db_articles)
    assert db_mock.commit.called_once()
