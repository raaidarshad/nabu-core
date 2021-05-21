"""
Pipeline that takes FeedData as input and outputs Articles. The input comes from constants, and the output
goes to a Postgres DB.

IOManagers
1. FeedData input
2. Article dataset output

Solids
1. get_feeds: <input> -> Feeds
    2. get_feed: url, limit -> Feed
3. feed_to_articles: Feed -> Articles
    4. feed_to_entry: Feed -> Entry
    5. parse_article: Entry -> Article
"""
from dagster import ModeDefinition, pipeline

from etl.resources.database_client import local_database_client
from etl.resources.rss_parser import rss_parser
from etl.solids.extract_articles import get_all_sources, get_latest_feed

local_mode = ModeDefinition(
    name="local",
    resource_defs={"database_client": local_database_client, "rss_parser": rss_parser}
)
dev_mode = ModeDefinition(name="dev")
prod_mode = ModeDefinition(name="prod")
test_mode = ModeDefinition(name="test")


@pipeline(mode_defs=[local_mode, dev_mode, prod_mode, test_mode])
def extract_articles():
    sources = get_all_sources()
    feeds = sources.map(get_latest_feed)



