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

local_mode = ModeDefinition(name="local")
dev_mode = ModeDefinition(name="dev")
prod_mode = ModeDefinition(name="prod")
test_mode = ModeDefinition(name="test")


@pipeline(mode_defs=[local_mode, dev_mode, prod_mode, test_mode])
def extract_articles():
    pass
