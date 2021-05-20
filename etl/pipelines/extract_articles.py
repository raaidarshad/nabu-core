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

local_mode = ModeDefinition(
    name="local",
    resource_defs={"database_client": local_database_client}
)
dev_mode = ModeDefinition(name="dev")
prod_mode = ModeDefinition(name="prod")
test_mode = ModeDefinition(name="test")


@pipeline(mode_defs=[local_mode, dev_mode, prod_mode, test_mode])
def extract_articles():
    pass
