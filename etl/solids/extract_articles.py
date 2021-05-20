from requests import Response
from typing import Iterator

from dagster import solid

from etl.models import Article, Feed, FeedEntry, Source


@solid
def get_all_sources(context) -> Iterator[Source]:
    # hits db to get all Sources
    pass


def get_latest_feed(source: Source) -> Feed:
    # uses feedparser to get rss Feed
    pass


def filter_to_updated_feeds():
    # filter out feeds that haven't been updated since last time?
    pass


def extract_entries(feed: Feed) -> Iterator[FeedEntry]:
    # get all entries from feed
    pass


def filter_out_old_entries():
    # something to filter to just entries we haven't seen before TODO
    pass


def get_article_response(feed_entry: FeedEntry) -> Response:
    # hit url for response
    pass


def extract_article(feed_entry: FeedEntry, response: Response) -> Article:
    # create Article object from feed_entry metadata and parsed content of response
    pass


def collect_articles():
    # gather all articles into one array?
    pass


def load_articles():
    # take the collected articles and put them in the db
    pass
