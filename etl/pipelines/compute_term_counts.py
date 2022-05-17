from dagster import AssetKey, EventLogEntry, ModeDefinition, PresetDefinition, RunRequest, \
    SensorEvaluationContext, asset_sensor, pipeline

from etl.common import datetime_to_str, get_current_time, ptb_retry_policy
from etl.resources.database_client import cloud_database_client, local_database_client, \
    compute_counts_test_database_client
from etl.solids.compute_term_counts import get_parsed_content, compute_counts, load_term_counts

# resources
cloud_resource_defs = {"database_client": cloud_database_client}
local_resource_defs = {"database_client": local_database_client}
test_resource_defs = {"database_client": compute_counts_test_database_client}

# modes
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# presets
main_preset = PresetDefinition(name="main", mode="local")
now = datetime_to_str(get_current_time())
timed_preset = PresetDefinition(name="timed",
                                mode="local",
                                run_config={
                                    "solids": {
                                        "get_parsed_content": {"config": {"begin": now,
                                                                          "end": now}},
                                        "compute_counts": {"config": {"runtime": now}},
                                        "load_term_counts": {"config": {"runtime": now}}}
                                })


# pipelines
@pipeline(mode_defs=[cloud_mode, local_mode, test_mode],
          preset_defs=[main_preset, timed_preset],
          solid_retry_policy=ptb_retry_policy,
          tags={"table": "termcount"})
def compute_term_counts():
    parsed_content = get_parsed_content()
    term_counts = compute_counts(parsed_content)
    load_term_counts(term_counts)


# sensors
@asset_sensor(asset_key=AssetKey("parsedcontent_table"), pipeline_name="compute_term_counts", mode="cloud")
def compute_counts_sensor(context: SensorEvaluationContext, asset_event: EventLogEntry):
    runtime_tag = asset_event.dagster_event.event_specific_data.materialization.tags["runtime"]

    yield RunRequest(
        run_key=context.cursor,
        run_config={
            "solids": {
                "get_parsed_content": {"config": {"begin": runtime_tag,
                                                  "end": runtime_tag}},
                "compute_counts": {"config": {"runtime": runtime_tag}},
                "load_term_counts": {"config": {"runtime": runtime_tag}}}
        },
    )
