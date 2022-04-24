from datetime import timedelta, timezone

from dagster import ModeDefinition, PresetDefinition, ScheduleExecutionContext, pipeline, schedule

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import cloud_database_client, local_database_client, \
    compute_clusters_test_database_client
from etl.solids.compute_article_clusters import get_term_counts, compute_tfidf, cluster_articles,\
    load_article_clusters, truncate_term_count

cloud_resource_defs = {"database_client": cloud_database_client}
local_resource_defs = {"database_client": local_database_client}
test_resource_defs = {"database_client": compute_clusters_test_database_client}

# modes
cloud_mode = ModeDefinition(name="cloud", resource_defs=cloud_resource_defs)
local_mode = ModeDefinition(name="local", resource_defs=local_resource_defs)
test_mode = ModeDefinition(name="test", resource_defs=test_resource_defs)

# presets
raw_now = get_current_time()
begin = datetime_to_str(raw_now - timedelta(hours=1))
now = datetime_to_str(raw_now)
timed_preset = PresetDefinition(
    mode="local",
    name="timed",
    run_config={
        "solids": {
            "get_term_counts": {"config": {"begin": begin, "end": now}},
            "cluster_articles": {"config": {"runtime": now,
                                            "cluster_type": "Agglomerative",
                                            "cluster_parameters": {"distance_threshold": 0.2, "n_clusters": None},
                                            "begin": begin,
                                            "end": now
                                            }},
            "load_article_clusters": {"config": {"runtime": now}}
        }}
)


# pipelines
@pipeline(mode_defs=[cloud_mode, local_mode, test_mode], preset_defs=[timed_preset], tags={"table": "articlecluster"})
def compute_article_clusters():
    counts = get_term_counts()
    tfidf = compute_tfidf(counts)
    clusters = cluster_articles(tfidf)
    loaded_rows = load_article_clusters(clusters)
    truncate_term_count(loaded_rows)


# schedules/sensors
@schedule(cron_schedule="0 * * * *", pipeline_name="compute_article_clusters", mode="cloud")
def article_cluster_schedule_12h(context: ScheduleExecutionContext):
    runtime = context.scheduled_execution_time
    if not runtime.tzinfo:
        runtime = runtime.astimezone(tz=timezone.utc)
    # for cluster_range in [{"days": 1}]:
    cluster_range = {"hours": 12}
    begin = datetime_to_str(runtime - timedelta(**cluster_range))
    runtime = datetime_to_str(runtime)
    return {
            "solids": {
                "get_term_counts": {"config": {"begin": begin, "end": runtime}},
                "cluster_articles": {"config": {"runtime": runtime,
                                                "cluster_type": "PTB0",
                                                "cluster_parameters": {"threshold": 0.45},
                                                "begin": begin,
                                                "end": runtime
                                                }},
                "load_article_clusters": {"config": {"runtime": runtime,
                                                     "cluster_range": cluster_range}}
            }}


@schedule(cron_schedule="*/5 * * * *", pipeline_name="compute_article_clusters", mode="cloud")
def article_cluster_schedule_1d(context: ScheduleExecutionContext):
    runtime = context.scheduled_execution_time
    if not runtime.tzinfo:
        runtime = runtime.astimezone(tz=timezone.utc)
    cluster_range = {"days": 1}
    begin = datetime_to_str(runtime - timedelta(**cluster_range))
    runtime = datetime_to_str(runtime)
    return {
            "solids": {
                "get_term_counts": {"config": {"begin": begin, "end": runtime}},
                "cluster_articles": {"config": {"runtime": runtime,
                                                "cluster_type": "PTB0",
                                                "cluster_parameters": {"threshold": 0.45},
                                                "begin": begin,
                                                "end": runtime
                                                }},
                "load_article_clusters": {"config": {"runtime": runtime,
                                                     "cluster_range": cluster_range}}
            }}


@schedule(cron_schedule="0 */6 * * *", pipeline_name="compute_article_clusters", mode="cloud")
def article_cluster_schedule_3d(context: ScheduleExecutionContext):
    runtime = context.scheduled_execution_time
    if not runtime.tzinfo:
        runtime = runtime.astimezone(tz=timezone.utc)
    # for cluster_range in [{"days": 1}]:
    cluster_range = {"days": 3}
    begin = datetime_to_str(runtime - timedelta(**cluster_range))
    runtime = datetime_to_str(runtime)
    return {
            "solids": {
                "get_term_counts": {"config": {"begin": begin, "end": runtime}},
                "cluster_articles": {"config": {"runtime": runtime,
                                                "cluster_type": "PTB0",
                                                "cluster_parameters": {"threshold": 0.45},
                                                "begin": begin,
                                                "end": runtime
                                                }},
                "load_article_clusters": {"config": {"runtime": runtime,
                                                     "cluster_range": cluster_range}}
            }}
