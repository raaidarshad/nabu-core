from dagster import ModeDefinition, PresetDefinition, pipeline

from etl.resources.database_client import local_database_client, compute_clusters_test_database_client
from etl.solids.compute_clusters import get_counts, compute_similarity, compute_and_load_clusters

local_resource_defs = {"database_client": local_database_client}
test_resource_defs = {"database_client": compute_clusters_test_database_client}

# modes
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# 1440 minutes = 1 day
minute_span = 1440
filter_threshold = 0.45

main_preset = PresetDefinition(
    mode="test",
    name="main_preset",
    run_config={"solids": {
        "get_counts": {"config": {"minute_span": minute_span}},
        "compute_similarity": {"config": {"filter_threshold": filter_threshold}},
        "compute_clusters_solid": {"config": {"minute_span": minute_span}}
    }}
)


@pipeline(mode_defs=[local_mode, test_mode], preset_defs=[main_preset])
def compute_clusters():
    counts = get_counts()
    similarity = compute_similarity(counts)
    compute_and_load_clusters(similarity)
