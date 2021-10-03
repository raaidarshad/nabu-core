from dagster import PipelineExecutionResult, execute_pipeline
import pytest

from etl.pipelines.load_sources import load_sources, load_rss_feeds


@pytest.mark.order(1)
def test_load_sources():
    result: PipelineExecutionResult = execute_pipeline(
        load_sources,
        mode="local",
        run_config={
            "solids": {
                "create_tables": {
                    "config": {
                        "path": "db"
                    }
                }
            }
        }
    )

    assert result.success

    # then add a source and make sure the pipeline doesn't break when updating
    # and that trying to insert an existing thing simply no-ps

    result: PipelineExecutionResult = execute_pipeline(
        load_sources,
        mode="local",
        run_config={
            "solids": {
                "create_tables": {
                    "config": {
                        "path": "db/test_files"
                    }
                }
            }
        }
    )

    assert result.success


@pytest.mark.order(2)
def test_load_rss_feeds():
    result: PipelineExecutionResult = execute_pipeline(
        load_rss_feeds,
        mode="local",
        run_config={
            "solids": {
                "create_tables": {
                    "config": {
                        "path": "db"
                    }
                }
            }
        }
    )

    assert result.success

    # then add a source and make sure the pipeline doesn't break when updating
    # and that trying to insert an existing thing simply no-ps

    result: PipelineExecutionResult = execute_pipeline(
        load_rss_feeds,
        mode="local",
        run_config={
            "solids": {
                "create_tables": {
                    "config": {
                        "path": "db/test_files"
                    }
                }
            }
        }
    )

    assert result.success
