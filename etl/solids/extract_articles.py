import concurrent.futures
import datetime
import requests
from uuid import UUID

from dagster import solid
from sqlalchemy.orm import Session

from etl.common import Context
from etl.db.models import Article as DbArticle, Source as DbSource
from etl.models import Article, Feed, FeedEntry, Source
from etl.resources.html_parser import BaseParser


@solid(required_resource_keys={"database_client"})
def get_all_sources(context: Context) -> list[Source]:
    # TODO might need to cast to pydantic type here? idk if dagster will like this
    db_client: Session = context.resources.database_client
    sources = db_client.query(DbSource).all()
    context.log.info(f"Got {len(sources)} sources")
    return sources


@solid(required_resource_keys={"rss_parser"})
def get_latest_feeds(context: Context, sources: list[Source]) -> list[Feed]:

    def _get_latest_feed(source: Source) -> Feed:
        # TODO wrap in try/except to handle when retrieval/parsing unsuccessful
        raw = context.resources.rss_parser.parse(source.rss_url)
        entries = [FeedEntry(**e) for e in raw.entries]
        return Feed(entries=entries, source_id=source.id, **raw.feed)

    return [_get_latest_feed(source) for source in sources]


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


@solid
def filter_to_new_entries(context: Context, feeds: list[Feed]) -> list[FeedEntry]:

    def time_filter(entry: FeedEntry, later_than: datetime.datetime) -> bool:
        return entry.published_at > later_than

    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=15)
    entries = []
    for feed in feeds:
        entries.extend([entry for entry in feed.entries if time_filter(entry, time_threshold)])
    context.log.info(f"Filtered down to {len(entries)} entries that were published since {time_threshold}")
    return entries


@solid(required_resource_keys={"http_client", "html_parser"})
def extract_articles(context: Context, entries: list[FeedEntry], source_map: dict[UUID, Source]) -> list[Article]:

    def _get_response_for_entry(feed_entry: FeedEntry) -> requests.Response:
        # TODO wrap in try/except, handle error cases
        # TODO need to do whole concurrent futures thing, rethink resources for this one? idk
        http_session: requests.Session = context.resources.http_client
        return http_session.get(feed_entry.url)

    def _get_article_from_response(
            response: requests.Response,
            feed_entry: FeedEntry) -> Article:
        parser: BaseParser = context.resources.html_parser
        # TODO make try/except better here
        source = source_map[feed_entry.source_id]
        try:
            text = parser.extract(content=response.content, parse_config=source.html_parser_config)
        except:
            context.log.info(f"Entry with URL {feed_entry.url} was not parsed successfully")
            text = feed_entry.summary
        return Article(parsed_content=text, **feed_entry.dict())

    def _extract_article(feed_entry: FeedEntry) -> Article:
        return _get_article_from_response(response=_get_response_for_entry(feed_entry), feed_entry=feed_entry)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        articles = executor.map(_extract_article, entries)
        return list(articles)


@solid(required_resource_keys={"database_client"})
def load_articles(context: Context, articles: list[Article]):
    # take the collected articles and put them in the db
    db_client: Session = context.resources.database_client
    db_articles = [DbArticle(**article.dict()) for article in articles]
    db_client.add_all(db_articles)
    db_client.commit()
