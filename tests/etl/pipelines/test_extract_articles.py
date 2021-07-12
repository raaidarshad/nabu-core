from datetime import datetime, timezone

from dagster import PipelineExecutionResult, execute_pipeline

from etl.pipelines.extract_articles import extract_articles


def test_extract_articles():
    result: PipelineExecutionResult = execute_pipeline(
        extract_articles,
        mode="test",
        run_config={
            "solids": {
                "get_latest_feeds": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc))
                    }
                },
                "filter_to_new_entries": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc))
                    }
                }
            }
        }
    )

    assert result.success
