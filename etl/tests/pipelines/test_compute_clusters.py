from dagster import PipelineExecutionResult, execute_pipeline

from etl.pipelines.compute_clusters import compute_clusters


def test_compute_clusters():
    result: PipelineExecutionResult = execute_pipeline(
        compute_clusters,
        mode="test",
        run_config={
            "solids":
                {
                    "get_counts": {"config": {"minute_span": 1440}},
                    "compute_similarity": {"config": {"filter_threshold": 0.45}},
                    "compute_and_load_clusters": {"config": {"minute_span": 1440}}
                }
        }
    )

    assert result.success
