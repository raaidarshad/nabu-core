from dagster import AssetKey, EventLogEntry, ModeDefinition, PresetDefinition, RunRequest, SensorEvaluationContext, \
    asset_sensor, pipeline

from etl.common import get_current_time, datetime_to_str
from etl.resources.database_client import cloud_database_client, local_database_client, \
    extract_articles_test_database_client
from etl.resources.http_client import http_client, mock_http_client
from etl.resources.thread_local import thread_local, mock_thread_local
from etl.solids.extract_raw_article_content import get_articles, request_raw_content, load_raw_content

# resource definitions
cloud_resource_defs = {
    "database_client": cloud_database_client,
    "http_client": http_client,
    "thread_local": thread_local
}

local_resource_defs = {
    "database_client": local_database_client,
    "http_client": http_client,
    "thread_local": thread_local
}

test_resource_defs = {
    "database_client": extract_articles_test_database_client,
    "http_client": mock_http_client,
    "thread_local": mock_thread_local
}
# mode definitions
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# preset definitions
main_preset = PresetDefinition(name="main_preset", mode="local")


# pipelines
@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[main_preset], tags={"table": "rawcontent"})
def extract_raw_article_content():
    articles = get_articles()
    raw_content = request_raw_content(articles)
    load_raw_content(raw_content)


# schedules/sensors
@asset_sensor(asset_key=AssetKey("article_table"), pipeline_name="extract_raw_article_content", mode="cloud")
def extract_new_article_raw_content(context: SensorEvaluationContext, asset_event: EventLogEntry):
    article_runtime_tag = asset_event.dagster_event.event_specific_data.materialization.tags["runtime"]
    raw_content_runtime = datetime_to_str(get_current_time())

    yield RunRequest(
        run_key=context.cursor,
        run_config={
            "solids": {
                # we specify both begin and end as the same so it operates in "batch" or "tag" mode,
                # where we use the exact timestamp as a batch tag to pull the right articles
                "get_articles": {"config": {"begin": article_runtime_tag, "end": article_runtime_tag}},
                "request_raw_content": {"config": {"runtime": raw_content_runtime}},
                "load_raw_content": {"config": {"runtime": raw_content_runtime}}
            }
        }
    )
