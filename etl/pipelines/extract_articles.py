"""
Pipeline that gets all Sources from DB and writes newly published Articles to DB.
"""
from dagster import ModeDefinition, pipeline

from etl.resources import local_database_client, html_parser, http_client, rss_parser, thread_local
from etl.solids.extract_articles import get_all_sources, get_latest_feeds, filter_to_updated_feeds, \
    filter_to_new_entries, extract_articles, load_articles


common_resource_defs = {
        "rss_parser": rss_parser,
        "http_client": http_client,
        "thread_local": thread_local,
        "html_parser": html_parser
    }

local_resource_defs = common_resource_defs
local_resource_defs["database_client"] = local_database_client

local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
# dev_mode = ModeDefinition(name="dev")
# prod_mode = ModeDefinition(name="prod")
# test_mode = ModeDefinition(name="test")


@pipeline(mode_defs=[local_mode])
def extract_articles():
    sources = get_all_sources()
    source_map = {s.id: s for s in sources}

    feeds = get_latest_feeds(sources)
    filtered_feeds = filter_to_updated_feeds(feeds)
    filtered_entries = filter_to_new_entries(filtered_feeds)
    articles = extract_articles(filtered_entries, source_map)
    load_articles(articles)






