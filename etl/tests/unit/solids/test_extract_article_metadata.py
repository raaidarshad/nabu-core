from datetime import timedelta
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid
import feedparser

from etl.common import clean_text, get_source_names, get_current_time, datetime_to_str
from etl.resources.database_client import mock_database_client
from etl.resources.rss_parser import mock_rss_parser
from etl.solids.extract_article_metadata import get_raw_feed_entries, get_raw_feeds, get_rss_feeds, get_sources,\
    load_articles, transform_raw_feed_entries_to_articles
from ptbmodels.models import Article, RawFeed, RawFeedEntry, RssFeed, Source


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
        mode_def=ModeDefinition(name="test",
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
    source_names = get_source_names()[:3]
    expected_rss_feeds = [
        RssFeed(
            source_id=idx,
            url=f"https://{n}.com",
            parser_config={"fake": "config"}
        ) for idx, n in enumerate(source_names)]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_rss_feeds)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_rss_feeds,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        run_config={
            "solids": {
                "get_rss_feeds": {
                    "config": {
                        "sources": source_names
                    }
                }
            }
        }
    )

    assert result.success
    assert result.output_value() == expected_rss_feeds


def test_get_raw_feeds():
    source_names = get_source_names()[:3]

    rss_feeds = [
        RssFeed(
            source_id=idx,
            url="https://fake.com",
            parser_config={"fake": "config"}
        ) for idx, n in enumerate(source_names)]

    parsed = feedparser.FeedParserDict({
        "status": 200,
        "feed": feedparser.FeedParserDict(
            {"updated": datetime_to_str(get_current_time()),
             "link": "https://www.fake.com",
             "title": "myfeed_title",
             "subtitle": "myfeed_subtitle"
             }),
        "entries": [feedparser.FeedParserDict(
            {"title": "fake_title",
             "summary": "fake_summary",
             "published": datetime_to_str(get_current_time()),
             "link": "https://www.fake.com",
             "author": "pencil mcpen"
             })]
    })

    def _test_rss_parser(_init_context):
        rss_mock = mock_rss_parser()
        rss_mock.parse = Mock(return_value=parsed)
        return rss_mock

    result: SolidExecutionResult = execute_solid(
        get_raw_feeds,
        input_values={"rss_feeds": rss_feeds},
        mode_def=ModeDefinition(name="test",
                                resource_defs={"rss_parser": ResourceDefinition(_test_rss_parser)})
    )

    assert result.success
    assert len(result.output_value()) == len(rss_feeds)
    for idx, output in enumerate(result.output_value()):
        assert isinstance(output, RawFeed)
        assert output == RawFeed(title=parsed.feed.title,
                                 subtitle=parsed.feed.subtitle,
                                 entries=[
                                     RawFeedEntry(
                                         title=parsed.entries[0].title,
                                         summary=parsed.entries[0].summary,
                                         published_at=parsed.entries[0].published,
                                         link=parsed.entries[0].link,
                                         author=parsed.entries[0].author,
                                         source_id=rss_feeds[idx].source_id,
                                         rss_feed_id=rss_feeds[idx].id
                                     )
                                 ],
                                 link=parsed.feed.link,
                                 source_id=rss_feeds[idx].source_id,
                                 rss_feed_id=rss_feeds[idx].id)


def test_get_new_raw_feed_entries():
    entries = [
        RawFeedEntry(
            title=f"rfe{idx}",
            published_at=get_current_time(),
            link=f"https://fake{idx}.com",
            source_id=idx,
            rss_feed_id=uuid4()
        )
        for idx in range(10)
    ]

    raw_feeds = [
        RawFeed(
            title="title1",
            entries=entries[:4],
            link="https://fake1.com",
            source_id=1,
            rss_feed_id=uuid4()
        ),
        RawFeed(
            title="title2",
            entries=entries[4:],
            link="https://fake2.com",
            source_id=2,
            rss_feed_id=uuid4()
        )
    ]

    result: SolidExecutionResult = execute_solid(
        get_raw_feed_entries,
        input_values={"raw_feeds": raw_feeds}
    )

    assert result.success
    assert result.output_value() == entries


def test_transform_raw_feed_entries_to_articles():
    def _summary_if_idx_even(idx: int):
        if idx % 2 == 0:
            return "<p>textytexttext</p>"

    entries = [
        RawFeedEntry(
            title=f"rfe{idx}",
            summary=_summary_if_idx_even(idx),
            published_at=get_current_time(),
            link=f"https://fake{idx}.com",
            source_id=idx,
            rss_feed_id=uuid4()
        )
        for idx in range(10)
    ]

    result: SolidExecutionResult = execute_solid(
        transform_raw_feed_entries_to_articles,
        input_values={"raw_feed_entries": entries}
    )

    assert result.success
    assert len(result.output_value()) == len(entries)
    for idx, res in enumerate(result.output_value()):
        assert res.title == entries[idx].title
        assert res.published_at == entries[idx].published_at
        assert res.url == entries[idx].url
        assert res.summary in [entries[idx].title, clean_text(entries[idx].summary)]
        assert res.source_id == entries[idx].source_id
        assert res.rss_feed_id == entries[idx].rss_feed_id


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
        input_values={"entities": articles}
    )

    assert result.success
    assert result.output_value() == articles
    # count of rows in mock should be the same, therefore no asset should be materialized
    assert result.materializations_during_compute == []
    assert db_mock.exec.called_once()
    assert db_mock.commit.called_once()
