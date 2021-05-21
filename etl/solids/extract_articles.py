import datetime
import requests

from dagster import solid
from dagster.experimental import DynamicOutput, DynamicOutputDefinition

from etl.common import Context
from etl.db.models import Source as DbSource
from etl.models import Article, Feed, FeedEntry, Source
from etl.resources.html_parser import BaseParser


@solid(required_resource_keys={"database_client"}, output_defs=[DynamicOutputDefinition(Source)])
def get_all_sources(context: Context):
    # TODO might need to cast to pydantic type here? idk if dagster will like this
    sources = context.resources.database_client.query(DbSource).all()
    context.log.info(f"Got {len(sources)} sources")
    for src in sources:
        yield DynamicOutput(value=src, mapping_key=str(src.id))


@solid(required_resource_keys={"rss_parser"})
def get_latest_feed(context: Context, source: Source) -> Feed:
    # TODO wrap in try/except to handle when retrieval/parsing unsuccessful
    raw = context.resources.rss_parser.parse(source.rss_url)
    entries = [FeedEntry(**e) for e in raw.entries]
    return Feed(entries=entries, source_id=source.id, **raw.feed)


@solid
def filter_to_updated_feeds(context: Context, feeds: list[Feed]) -> list[Feed]:
    # TODO timezones? also, "N" minutes? get from context?

    def time_filter(feed: Feed, later_than: datetime.datetime) -> bool:
        return feed.updated_at > later_than

    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=15)
    filtered = [f for f in feeds if time_filter(f, time_threshold)]
    context.log.info(f"Started with {len(feeds)} feeds")
    context.log.info(f"Filtered down to {len(filtered)} feeds updated since {time_threshold}")
    return filtered


def filter_out_old_entries():
    # something to filter to just entries we haven't seen before TODO
    pass


@solid(required_resource_keys={"http_client"})
def get_article_response(context: Context, feed_entry: FeedEntry) -> requests.Response:
    # TODO wrap in try/except, handle error cases
    http_session: requests.Session = context.resources.http_client
    return http_session.get(feed_entry.url)


@solid(required_resource_keys={"html_parser"})
def extract_article(
        context: Context,
        response: requests.Response,
        feed_entry: FeedEntry,
        source: Source) -> Article:
    parser: BaseParser = context.resources.html_parser
    # TODO make try/except better here
    try:
        text = parser.extract(content=response.content, parse_config=source.html_parser_config)
    except:
        context.log.info(f"Entry with URL {feed_entry.url} was not parsed successfully")
        text = feed_entry.summary
    return Article(source_id=source.id, parsed_content=text, **feed_entry.dict())


def collect_articles(context: Context):
    # gather all articles into one array?
    pass


def load_articles(context: Context):
    # take the collected articles and put them in the db
    pass
