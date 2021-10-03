from dagster import PipelineExecutionResult, execute_pipeline

from etl.pipelines.load_sources import load_sources, load_rss_feeds


def test_load_sources_and_rss_feeds():
    result: PipelineExecutionResult = execute_pipeline(
        load_sources,
        mode="local",
        run_config={
            "solids": {
                "create_tables": {
                    "config": {
                        "path": "etl/db"
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
                        "path": "etl/db/test_files"
                    }
                }
            }
        }
    )

    assert result.success

    result: PipelineExecutionResult = execute_pipeline(
        load_rss_feeds,
        mode="local",
        run_config={
            "solids": {
                "create_tables": {
                    "config": {
                        "path": "etl/db"
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
                        "path": "etl/db/test_files"
                    }
                }
            }
        }
    )

    assert result.success
