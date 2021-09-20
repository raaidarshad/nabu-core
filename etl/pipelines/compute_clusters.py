from dagster import AssetKey, ModeDefinition, PresetDefinition, RunRequest, \
    SensorEvaluationContext, asset_sensor, pipeline

from etl.resources.database_client import cloud_database_client, local_database_client, \
    compute_clusters_test_database_client
from etl.solids.compute_clusters import get_counts, compute_similarity, compute_and_load_clusters

cloud_resource_defs = {"database_client": cloud_database_client}
local_resource_defs = {"database_client": local_database_client}
test_resource_defs = {"database_client": compute_clusters_test_database_client}

# modes
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# 1440 minutes = 1 day
day_minute_span = 1440
week_minute_span = day_minute_span * 7
filter_threshold = 0.45

# presets
main_preset = PresetDefinition(
    mode="cloud",
    name="main_preset",
    run_config={"solids": {
        "get_counts": {"config": {"minute_span": day_minute_span}},
        "compute_similarity": {"config": {"filter_threshold": filter_threshold}},
        "compute_and_load_clusters": {"config": {"minute_span": day_minute_span}}
    }}
)


# sensors
@asset_sensor(asset_key=AssetKey("count_table"), pipeline_name="compute_clusters", mode="cloud")
def count_table_day_sensor(context: SensorEvaluationContext, asset_event):
    yield _run_generator(day_minute_span, context.cursor)


@asset_sensor(asset_key=AssetKey("count_table"), pipeline_name="compute_clusters", mode="cloud")
def count_table_week_sensor(context: SensorEvaluationContext, asset_event):
    yield _run_generator(week_minute_span, context.cursor)


def _run_generator(minute_span: int, run_key) -> RunRequest:
    return RunRequest(
        run_key=run_key,
        run_config={
            "solids": {
                "get_counts": {"config": {"minute_span": minute_span}},
                "compute_similarity": {"config": {"filter_threshold": filter_threshold}},
                "compute_and_load_clusters": {"config": {"minute_span": minute_span}}
            }
        }
    )


@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[main_preset], tags={"table": "cluster"})
def compute_clusters():
    counts = get_counts()
    similarity = compute_similarity(counts)
    compute_and_load_clusters(similarity)
