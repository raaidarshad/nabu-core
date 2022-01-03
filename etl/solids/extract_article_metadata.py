import pydantic
from dagster import Array, Enum, EnumValue, Field, solid

from sqlmodel import Session, select, update

from etl.common import DagsterTime, Context, clean_text, get_source_names, load_rows_factory, str_to_datetime
from ptbmodels.models import Article, RawFeed, RawFeedEntry, RssFeed, Source

# we want to restrict developer selection of source by name to only source names that we know of, so we use an Enum
SourceDenum = Enum("SourceDenum", [EnumValue("all")] + [EnumValue(n) for n in get_source_names()])

SourceDenumConfig = Field(
    config=Array(SourceDenum),
    # if no source names provided, we will simply ask for all sources
    default_value=["all"],
    is_required=False
)


@solid(required_resource_keys={"database_client"}, config_schema={"sources": SourceDenumConfig})
def get_sources(context: Context) -> list[Source]:
    db_client: Session = context.resources.database_client
    source_names = context.solid_config["sources"]
    if "all" in source_names:
        statement = select(Source)
    else:
        statement = select(Source).where(Source.name.in_(source_names))
    context.log.info(f"Attempting to execute: {statement}")
    sources = db_client.exec(statement).all()
    context.log.info(f"Got {len(sources)} sources")
    return sources


@solid(required_resource_keys={"database_client"}, config_schema={"sources": SourceDenumConfig})
def get_rss_feeds(context: Context) -> list[RssFeed]:
    db_client: Session = context.resources.database_client
    source_names = context.solid_config["sources"]
    if "all" in source_names:
        statement = select(RssFeed).where(RssFeed.is_okay)
    else:
        statement = select(RssFeed).join(Source, RssFeed.source_id == Source.id).where(
            (Source.name.in_(source_names)) & (RssFeed.is_okay))
    context.log.info(f"Attempting to execute: {statement}")
    feeds = db_client.exec(statement).all()
    context.log.info(f"Got {len(feeds)} feeds")
    return feeds


@solid(required_resource_keys={"rss_parser", "database_client"})
def get_raw_feeds(context: Context, rss_feeds: list[RssFeed]) -> list[RawFeed]:
    def _get_raw_feed(rss_feed: RssFeed) -> RawFeed:
        raw = context.resources.rss_parser.parse(rss_feed.url)
        # if okay, parse entries
        if raw.status == 200:
            entries = [RawFeedEntry(
                source_id=rss_feed.source_id,
                rss_feed_id=rss_feed.id,
                published_at=str_to_datetime(e.published),
                **e) for e in raw.entries]
            try:
                return RawFeed(
                    entries=entries,
                    source_id=rss_feed.source_id,
                    rss_feed_id=rss_feed.id,
                    title=raw.feed.title,
                    # this is still aliased as 'link' in the model because we used to
                    # unpack the whole raw.feed object into this; couldn't hurt to update
                    # the model and all uses of it to say url and remove the alias
                    link=rss_feed.url
                )
            except pydantic.ValidationError as e:
                context.log.debug(f"The error: {e}, for rss_feed of id {rss_feed.id} and url {rss_feed.url}")
                context.log.debug(f"The raw.feed values of concern are: {raw.feed}")

        # see https://pythonhosted.org/feedparser/http-redirect.html for details for 301 and 410 codes
        elif raw.status in [301, 410]:
            db_client: Session = context.resources.database_client
            if raw.status == 301:
                # if 310 or "permanent redirect", update rss feed url
                statement = update(RssFeed).where(RssFeed.id == rss_feed.id).values(url=raw.href)
            else:
                # if 410 or "gone", set rss feed column of is_okay to False so we don't use it
                statement = update(RssFeed).where(RssFeed.id == rss_feed.id).values(is_okay=False)
            db_client.execute(statement)
            db_client.commit()
        else:
            context.log.warning(f"RssFeed with url {rss_feed.url} not parsed, code: {raw.status}")

    raw_feeds = list(filter(None, [_get_raw_feed(rss_feed) for rss_feed in rss_feeds]))
    context.log.info(f"Got {len(raw_feeds)} raw rss feeds, expected {len(rss_feeds)}")
    return raw_feeds


@solid
def get_raw_feed_entries(context: Context, raw_feeds: list[RawFeed]) -> list[RawFeedEntry]:
    raw_feed_entries = []
    for raw_feed in raw_feeds:
        context.log.info(f"RawFeed with url {raw_feed.url} has {len(raw_feed.entries)} entries")
        raw_feed_entries.extend(raw_feed.entries)
    return raw_feed_entries


@solid(config_schema={"runtime": DagsterTime})
def transform_raw_feed_entries_to_articles(context: Context, raw_feed_entries: list[RawFeedEntry]) -> list[Article]:
    context.log.info(f"Transforming {len(raw_feed_entries)} RawFeedEntries to Articles")
    current_time = str_to_datetime(context.solid_config["runtime"])

    # sanitize inputs
    for rfe in raw_feed_entries:
        if rfe.authors:
            rfe.authors = clean_text(rfe.authors)
        rfe.title = clean_text(rfe.title)
        if rfe.summary:
            rfe.summary = clean_text(rfe.summary)
        else:
            rfe.summary = rfe.title

    return [Article(added_at=current_time, **rfe.dict()) for rfe in raw_feed_entries]


load_articles = load_rows_factory("load_articles", Article, [Article.url])
