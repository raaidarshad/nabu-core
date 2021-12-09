import os

from dagster import AssetKey, EventLogEntry, ModeDefinition, PresetDefinition, RunRequest, SensorEvaluationContext, \
    asset_sensor, pipeline

from etl.common import ptb_retry_policy
from etl.resources.boto_client import boto_client, mock_boto_client
from etl.resources.database_client import cloud_database_client, local_database_client, \
    write_latest_clusters_test_database_client
from etl.solids.write_latest_clusters import get_latest_clusters, prep_latest_clusters, write_to_bucket

# resource definitions
cloud_resource_defs = {
    "database_client": cloud_database_client,
    "boto_client": boto_client
}

local_resource_defs = {
    "database_client": local_database_client,
    "boto_client": mock_boto_client
}

test_resource_defs = {
    "database_client": write_latest_clusters_test_database_client,
    "boto_client": mock_boto_client
}

# mode definitions
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# preset definitions
main_preset = PresetDefinition(name="main", mode="local")


# pipelines
@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[main_preset], solid_retry_policy=ptb_retry_policy)
def write_latest_clusters():
    clusters = get_latest_clusters()
    prepped = prep_latest_clusters(clusters)
    write_to_bucket(prepped)


# schedules/sensors
@asset_sensor(asset_key=AssetKey("articlecluster_table"), pipeline_name="write_latest_clusters", mode="cloud")
def write_latest_clusters_sensor(context: SensorEvaluationContext, asset_event: EventLogEntry):
    yield RunRequest(
        run_key=context.cursor,
        run_config={
            "solids": {
                "write_to_bucket": {
                    "config": {"bucket": os.getenv("SPACES_BUCKET_NAME"), "key": os.getenv("LATEST_FILE_NAME", "latest.json")}}
            }
        }
    )
