from datetime import timedelta

from dagster import PipelineExecutionResult, execute_pipeline
import pytest

from etl.common import datetime_to_str, get_current_time
from etl.pipelines.compute_article_clusters import compute_article_clusters

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
