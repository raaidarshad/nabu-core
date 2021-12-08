from dagster import pipeline

from etl.resources.boto_client import boto_client, mock_boto_client
from etl.resources.database_client import cloud_database_client, local_database_client, \
    write_latest_clusters_test_database_client


# resource definitions
cloud_resource_defs = {
    "database_client": cloud_database_client,
    "boto_client": boto_client
}

local_resource_defs = {
    "database_client": local_database_client,
    "boto_client": boto_client
}

test_resource_defs = {
    "database_client": write_latest_clusters_test_database_client,
    "boto_client": mock_boto_client
}

# mode definitions

# preset definitions

# pipelines

# schedules/sensors
