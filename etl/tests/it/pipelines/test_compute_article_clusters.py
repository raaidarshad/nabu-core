from datetime import timedelta

from dagster import PipelineExecutionResult, execute_pipeline
import pytest

from etl.common import datetime_to_str, get_current_time
from etl.pipelines.compute_article_clusters import compute_article_clusters
from etl.pipelines.write_latest_clusters import write_latest_clusters

runtime = get_current_time()
begin = datetime_to_str(runtime - timedelta(minutes=5))
end = datetime_to_str(runtime + timedelta(minutes=1))
runtime = datetime_to_str(runtime)


@pytest.mark.order(7)
def test_compute_article_clusters():
    result: PipelineExecutionResult = execute_pipeline(
        compute_article_clusters,
        mode="local",
        run_config={
            "solids": {
                "get_term_counts": {"config": {"begin": begin, "end": end}},
                "cluster_articles": {"config": {"runtime": runtime,
                                                "cluster_type": "Agglomerative",
                                                "cluster_parameters": {"distance_threshold": 0.2, "n_clusters": None},
                                                "begin": begin,
                                                "end": end
                                                }},
                "load_article_clusters": {"config": {"runtime": runtime}}
            }}
    )

    assert result.success


# TODO figure out how to have this test run reliably
# @pytest.mark.order(8)
# def test_write_latest_clusters():
#     result: PipelineExecutionResult = execute_pipeline(
#         write_latest_clusters,
#         mode="local",
#         run_config={
#             "solids": {
#                 "write_to_bucket": {
#                     "config": {"bucket": "my-bucket", "key": "myfile.json"}}
#             }
#         }
#     )
#
#     assert result.success
