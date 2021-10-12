from dagster import AssetKey, ModeDefinition, PresetDefinition, RunRequest, \
    SensorEvaluationContext, asset_sensor, pipeline

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import cloud_database_client, local_database_client, \
    compute_clusters_test_database_client
from etl.solids.compute_article_clusters import get_term_counts, compute_tfidf, cluster_articles, load_article_clusters

cloud_resource_defs = {"database_client": cloud_database_client}
local_resource_defs = {"database_client": local_database_client}
test_resource_defs = {"database_client": compute_clusters_test_database_client}

# modes
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# presets
now = datetime_to_str(get_current_time())
timed_preset = PresetDefinition(
    mode="local",
    name="timed",
    run_config={"solids": {
        "get_term_counts": {"config": {"begin": now, "end": now}}},
        "cluster_articles": {"config": {"runtime": now,
                                        "cluster_type": "Agglomerative",
                                        "cluster_parameters": {"distance_threshold": 0.2},
                                        "begin": now,
                                        "end": now
                                        }},
        "load_article_clusters": {"config": {"runtime": now}}
    }
)


# sensors TODO, might want this to be on its own schedule now instead
# @asset_sensor(asset_key=AssetKey("count_table"), pipeline_name="compute_clusters", mode="cloud")
# def count_table_day_sensor(context: SensorEvaluationContext, asset_event):
#     yield _run_generator(day_minute_span, context.cursor)
#
#
# @asset_sensor(asset_key=AssetKey("count_table"), pipeline_name="compute_clusters", mode="cloud")
# def count_table_week_sensor(context: SensorEvaluationContext, asset_event):
#     yield _run_generator(week_minute_span, context.cursor)
#
#
# def _run_generator(minute_span: int, run_key) -> RunRequest:
#     return RunRequest(
#         run_key=run_key,
#         run_config={"solids": {
#             "get_term_counts": {"config": {"begin": now, "end": now}}},
#             "cluster_articles": {"config": {"runtime": now,
#                                             "cluster_type": "Agglomerative",
#                                             "cluster_parameters": {"distance_threshold": 0.2},
#                                             "begin": now,
#                                             "end": now
#                                             }},
#             "load_article_clusters": {"config": {"runtime": now}}
#         }
#     )


@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[timed_preset], tags={"table": "articlecluster"})
def compute_article_clusters():
    counts = get_term_counts()
    tfidf = compute_tfidf(counts)
    clusters = cluster_articles(tfidf)
    load_article_clusters(clusters)
