"""
Pipeline that gets all Sources from DB and writes newly published Articles to DB.
"""

from datetime import datetime, timedelta

from dagster import ModeDefinition, PresetDefinition, ScheduleExecutionContext, pipeline, schedule

from etl.resources.database_client import local_database_client
from etl.resources.html_parser import html_parser
from etl.resources.http_client import http_client
from etl.resources.rss_parser import rss_parser
from etl.resources.thread_local import thread_local
from etl.solids.extract_articles import get_all_sources, get_latest_feeds, create_source_map,\
    filter_to_new_entries, extract_articles, load_articles

# resources
common_resource_defs = {
    "rss_parser": rss_parser,
    "http_client": http_client,
    "thread_local": thread_local,
    "html_parser": html_parser
}

local_resource_defs = common_resource_defs
local_resource_defs["database_client"] = local_database_client

# modes
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)

# dev_mode = ModeDefinition(name="dev")
# prod_mode = ModeDefinition(name="prod")
# test_mode = ModeDefinition(name="test")

my_threshold = datetime.utcnow() - timedelta(minutes=15)
my_threshold = str(my_threshold)

main_preset = PresetDefinition(
    name="main_preset",
    run_config={"solids": {"get_latest_feeds": {"config": {"time_threshold": my_threshold}},
                       "filter_to_new_entries": {"config": {"time_threshold": my_threshold}}}},
    mode="local"
)


@pipeline(mode_defs=[local_mode], preset_defs=[main_preset])
def extract_articles():
    sources = get_all_sources()
    source_map = create_source_map(sources)

    feeds = get_latest_feeds(sources)
    filtered_entries = filter_to_new_entries(feeds)
    articles = extract_articles(filtered_entries, source_map)
    load_articles(articles)


# every 15 minutes
@schedule(cron_schedule="*/15 * * * *", pipeline_name="extract_articles", mode="local")
def main_schedule(context: ScheduleExecutionContext):
    threshold = context.scheduled_execution_time - timedelta(minutes=15)
    return {"solids": {"get_latest_feeds": {"config": {"time_threshold": threshold}},
                       "filter_to_new_entries": {"config": {"time_threshold": threshold}}}}
