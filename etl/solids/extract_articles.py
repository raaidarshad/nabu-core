from requests import Response
from typing import Iterator

from dagster import solid
from dagster.experimental import DynamicOutput, DynamicOutputDefinition

from etl.common import Context
from etl.db.models import Source as DbSource
from etl.models import Article, Feed, FeedEntry, Source


@solid(required_resource_keys={"database_client"}, output_defs=[DynamicOutputDefinition(Source)])
def get_all_sources(context: Context):
    # hits db to get all Sources
    sources = context.resources.database_client.query(DbSource).all()
    for src in sources:
        yield DynamicOutput(value=src, mapping_key=str(src.id))


@solid(required_resource_keys={"rss_parser"})
def get_latest_feed(context: Context, source: Source) -> Feed:
    # uses feedparser to get rss Feed
    raw = context.resources.rss_parser.parse(source.rss_url)
    entries = [FeedEntry(**e) for e in raw.entries]
    return Feed(entries=entries, **raw.feed)


def filter_to_updated_feeds():
    # filter out feeds that haven't been updated since last time?
    pass


def extract_entries(context: Context, feed: Feed) -> list[FeedEntry]:
    # get all entries from feed
    pass


def filter_out_old_entries():
    # something to filter to just entries we haven't seen before TODO
    pass


def get_article_response(context: Context, feed_entry: FeedEntry) -> Response:
    # hit url for response
    pass


def extract_article(context: Context, feed_entry: FeedEntry, response: Response) -> Article:
    # create Article object from feed_entry metadata and parsed content of response
    pass


def collect_articles(context: Context):
    # gather all articles into one array?
    pass


def load_articles(context: Context):
    # take the collected articles and put them in the db
    pass
