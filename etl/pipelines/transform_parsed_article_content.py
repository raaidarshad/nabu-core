from dagster import AssetKey, EventLogEntry, ModeDefinition, PresetDefinition, RunRequest, SensorEvaluationContext, \
    asset_sensor, pipeline

from etl.common import get_current_time, datetime_to_str
from etl.resources.database_client import cloud_database_client, local_database_client, \
    extract_articles_test_database_client
from etl.resources.html_parser import html_parser, mock_html_parser
from etl.solids.transform_parsed_article_content import get_raw_content, parse_raw_content, load_parsed_content

# resource definitions
cloud_resource_defs = {
    "database_client": cloud_database_client,
    "html_parser": html_parser,
}

local_resource_defs = {
    "database_client": local_database_client,
    "html_parser": html_parser,
}

test_resource_defs = {
    "database_client": extract_articles_test_database_client,
    "html_parser": mock_html_parser,
}
# mode definitions
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# preset definitions
main_preset = PresetDefinition(name="main", mode="local")
now = datetime_to_str(get_current_time())
timed_preset = PresetDefinition(name="timed",
                                mode="local",
                                run_config={
                                    "solids": {
                                        "get_raw_content": {"config": {"begin": now, "end": now}},
                                        "parse_raw_content": {"config": {"runtime": now}},
                                        "load_parsed_content": {"config": {"runtime": now}}
                                    }
                                })


# pipelines
@pipeline(mode_defs=[cloud_mode, local_mode, test_mode],
          preset_defs=[main_preset, timed_preset],
          tags={"table": "parsedcontent"})
def transform_parsed_article_content():
    raw_content = get_raw_content()
    parsed_content = parse_raw_content(raw_content)
    load_parsed_content(parsed_content)


# schedules/sensors
@asset_sensor(asset_key=AssetKey("rawcontent_table"), pipeline_name="transform_parsed_article_content", mode="cloud")
def transform_parsed_article_content_sensor(context: SensorEvaluationContext, asset_event: EventLogEntry):
    raw_content_runtime_tag = asset_event.dagster_event.event_specific_data.materialization.tags["runtime"]
    parsed_content_runtime = datetime_to_str(get_current_time())

    yield RunRequest(
        run_key=context.cursor,
        run_config={
            "solids": {
                # we specify both begin and end as the same so it operates in "batch" or "tag" mode,
                # where we use the exact timestamp as a batch tag to pull the right articles
                "get_raw_content": {"config": {"begin": raw_content_runtime_tag, "end": raw_content_runtime_tag}},
                "parse_raw_content": {"config": {"runtime": parsed_content_runtime}},
                "load_parsed_content": {"config": {"runtime": parsed_content_runtime}}
            }
        }
    )
