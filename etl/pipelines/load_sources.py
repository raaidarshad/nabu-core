from dagster import ModeDefinition, PresetDefinition, pipeline

from etl.resources.database_client import cloud_database_client, cloud_database_engine, local_database_client, \
    local_database_engine, mock_database_client, mock_database_engine
from etl.solids.load_sources import create_tables, get_rss_feeds_from_file, get_sources_from_file, load_rss_feed_rows, \
    load_source_rows


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
    mode="cloud",
    run_config={"solids": {"create_tables": {"config": {"path": "etl/db"}}}}
)


@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[main_preset], tags={"table": "source"})
def load_sources():
    path_format = create_tables()
    sources = get_sources_from_file(path_format=path_format)
    load_source_rows(sources)


@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[main_preset], tags={"table": "rssfeed"})
def load_rss_feeds():
    path_format = create_tables()
    rss_feeds = get_rss_feeds_from_file(path_format=path_format)
    load_rss_feed_rows(rss_feeds)

