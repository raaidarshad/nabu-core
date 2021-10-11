from datetime import timezone

from dagster import ModeDefinition, PresetDefinition, ScheduleExecutionContext, pipeline, schedule

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import cloud_database_client, local_database_client, \
    extract_articles_test_database_client
from etl.resources.rss_parser import mock_rss_parser, rss_parser
from etl.solids.extract_article_metadata import get_rss_feeds, get_raw_feeds, get_raw_feed_entries, \
    transform_raw_feed_entries_to_articles, load_articles

# resource definitions
cloud_resource_defs = {
    "database_client": cloud_database_client,
    "rss_parser": rss_parser
}

local_resource_defs = {
    "database_client": local_database_client,
    "rss_parser": rss_parser
}

test_resource_defs = {
    "database_client": extract_articles_test_database_client,
    "rss_parser": mock_rss_parser
}

# mode definitions
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# preset definitions
main_preset = PresetDefinition(name="main", mode="local")
timed_preset = PresetDefinition(name="timed",
                                mode="local",
                                run_config={
                                    "solids": {
                                        "transform_raw_feed_entries_to_articles": {
                                            "config": {"runtime": datetime_to_str(get_current_time())}},
                                        "load_articles": {
                                            "config": {"runtime": datetime_to_str(get_current_time())}}
                                    }})


# pipelines
@pipeline(mode_defs=[cloud_mode, local_mode, test_mode],
          preset_defs=[main_preset, timed_preset],
          tags={"table": "article"})
def extract_article_metadata():
    rss_feeds = get_rss_feeds()
    raw_feeds = get_raw_feeds(rss_feeds)
    raw_feed_entries = get_raw_feed_entries(raw_feeds)
    articles = transform_raw_feed_entries_to_articles(raw_feed_entries)
    load_articles(articles)


# schedules/sensors
@schedule(cron_schedule="13 */1 * * *", pipeline_name="extract_article_metadata", mode="cloud")
def main_schedule(context: ScheduleExecutionContext):
    runtime = context.scheduled_execution_time
    if not runtime.tzinfo:
        runtime = runtime.astimezone(tz=timezone.utc)
    return {"solids": {
        "transform_raw_feed_entries_to_articles": {"config": {"runtime": datetime_to_str(runtime)}},
        "load_articles": {"config": {"runtime": datetime_to_str(runtime)}}
    }}
