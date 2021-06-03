from datetime import datetime, timezone
from uuid import UUID, uuid4

from dagster import SolidExecutionResult, execute_solid

from etl.models import Article, Feed, FeedEntry, Source
from etl.pipelines.extract_articles import test_mode
from etl.solids.extract_articles import get_all_sources, create_source_map, get_latest_feeds, filter_to_new_entries, \
    extract_articles, load_articles

sources = [
    Source(id=uuid4(), name="source1", rss_url="https://fakeone.com/", html_parser_config={"id": "merp"}),
    Source(id=uuid4(), name="source2", rss_url="https://faketwo.com/", html_parser_config={"id": "merp"})
]


def test_get_all_sources():
    result: SolidExecutionResult = execute_solid(
        get_all_sources,
        mode_def=test_mode
    )

    assert result.success
    assert len(result.output_value()) == 1
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
    result: SolidExecutionResult = execute_solid(
        get_latest_feeds,
        mode_def=test_mode,
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


def test_filter_to_new_entries():
    result: SolidExecutionResult = execute_solid(
        filter_to_new_entries,
        mode_def=test_mode,
        input_values={
            "feeds": [
                Feed(title="feed1",
                     entries=[],
                     link="https://fake.com",
                     updated_at=datetime.now(timezone.utc),
                     source_id=uuid4())
            ]},
        run_config={
            "solids": {
                "filter_to_new_entries": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc))
                    }
                }
            }
        }
    )

    assert result.success


def test_extract_articles():
    sid = uuid4()
    result: SolidExecutionResult = execute_solid(
        extract_articles,
        mode_def=test_mode,
        input_values={
            "entries": [
                FeedEntry(title="entry1",
                          summary="summary",
                          published_at=datetime.now(timezone.utc),
                          link="https://fake.com",
                          author="pencil mcpen",
                          source_id=sid)
            ],
            "source_map": {
                sid: Source(id=uuid4(),
                            name="source1",
                            rss_url="https://fakeone.com/",
                            html_parser_config={"id": "merp"})}}
    )

    assert result.success


def test_load_articles():
    result: SolidExecutionResult = execute_solid(
        load_articles,
        mode_def=test_mode,
        input_values={
            "articles": [
                Article(id=uuid4(),
                        url="https://fake.com",
                        source_id=uuid4(),
                        title="title",
                        published_at=datetime.now(timezone.utc))
            ]}
    )

    assert result.success
