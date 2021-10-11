from datetime import datetime, timedelta, timezone

from dagster import PipelineExecutionResult, execute_pipeline

from etl.pipelines.compute_term_counts import compute_counts


def test_compute_counts():
    result: PipelineExecutionResult = execute_pipeline(
        compute_counts,
        mode="test",
        run_config={
            "solids": {
                "get_articles": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc) - timedelta(hours=1))
                    }
                }
            }
        }
    )

    assert result.success
