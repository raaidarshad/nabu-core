from dagster import AssetKey, ModeDefinition, PresetDefinition, RunRequest, SensorEvaluationContext, asset_sensor, \
    pipeline

from etl.resources.database_client import local_database_client, compute_clusters_test_database_client
from etl.solids.compute_clusters import get_counts, compute_similarity, compute_and_load_clusters

local_resource_defs = {"database_client": local_database_client}
test_resource_defs = {"database_client": compute_clusters_test_database_client}

# modes
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# 1440 minutes = 1 day
day_minute_span = 1440
filter_threshold = 0.45


# presets
main_preset = PresetDefinition(
    mode="test",
    name="main_preset",
    run_config={"solids": {
        "get_counts": {"config": {"minute_span": day_minute_span}},
        "compute_similarity": {"config": {"filter_threshold": filter_threshold}},
        "compute_and_load_clusters": {"config": {"minute_span": day_minute_span}}
    }}
)


# sensors
@asset_sensor(asset_key=AssetKey("count_table"), pipeline_name="compute_clusters", mode="local")
def count_table_sensor(context: SensorEvaluationContext, asset_event):
    yield RunRequest(
        run_key=context.cursor,
        run_config={
            "solids": {
                "get_counts": {"config": {"minute_span": day_minute_span}},
                "compute_similarity": {"config": {"filter_threshold": filter_threshold}},
                "compute_and_load_clusters": {"config": {"minute_span": day_minute_span}}
            }
        }
    )


@pipeline(mode_defs=[local_mode, test_mode], preset_defs=[main_preset])
def compute_clusters():
    counts = get_counts()
    similarity = compute_similarity(counts)
    compute_and_load_clusters(similarity)
