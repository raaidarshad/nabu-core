from dagster import ModeDefinition, pipeline

from etl.resources.database_client import local_database_client, mock_database_client
from etl.solids.compute_counts import get_articles, compose_rows, compute_count_matrix, load_counts


local_resource_defs = {
    "database_client": local_database_client
}

test_resource_defs = {
    "database_client": mock_database_client
}

# modes
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)


@pipeline(mode_defs=[local_mode, test_mode])
def compute_counts():
    articles = get_articles()
    count_matrix, features = compute_count_matrix(articles=articles)
    counts = compose_rows(articles=articles, features=features, count_matrix=count_matrix)
    load_counts(counts)
