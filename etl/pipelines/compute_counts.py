from datetime import datetime, timedelta

from dagster import ModeDefinition, PresetDefinition, pipeline

from etl.resources.database_client import local_database_client, compute_counts_test_database_client
from etl.solids.compute_counts import get_articles, compose_rows, compute_count_matrix, load_counts

local_resource_defs = {
    "database_client": local_database_client
}

test_resource_defs = {
    "database_client": compute_counts_test_database_client
}

# modes
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

my_threshold = datetime.utcnow() - timedelta(minutes=15)
my_threshold = str(my_threshold)

main_preset = PresetDefinition(
    mode="test",
    name="main_preset",
    run_config={"solids": {"get_articles": {"config": {"time_threshold": my_threshold}}}}
)


@pipeline(mode_defs=[local_mode, test_mode], preset_defs=[main_preset])
def compute_counts():
    articles = get_articles()
    count_matrix, features = compute_count_matrix(articles=articles)
    counts = compose_rows(articles=articles, features=features, count_matrix=count_matrix)
    load_counts(counts)
