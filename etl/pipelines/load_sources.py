from dagster import ModeDefinition, PresetDefinition, pipeline

from etl.resources.database_client import cloud_database_client, cloud_database_engine, local_database_client, \
    local_database_engine, mock_database_client, mock_database_engine
from etl.solids.load_sources import create_tables, load_sources_from_file


# resources
cloud_resource_defs = {
    "database_client": cloud_database_client,
    "database_engine": cloud_database_engine
}

local_resource_defs = {
    "database_client": local_database_client,
    "database_engine": local_database_engine
}

test_resource_defs = {
    "database_client": mock_database_client,
    "database_engine": mock_database_engine
}

# modes
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

main_preset = PresetDefinition(
    name="main_preset",
    mode="local"
)


@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[main_preset], tags={"table": "source"})
def load_sources():
    filepath = create_tables()
    load_sources_from_file(filepath=filepath)
