from dagster import PipelineExecutionResult, execute_pipeline
import pytest

from etl.common import datetime_to_str, get_current_time
from etl.pipelines.compute_term_counts import compute_term_counts
from etl.pipelines.extract_article_metadata import extract_article_metadata
from etl.pipelines.extract_raw_article_content import extract_raw_article_content
from etl.pipelines.transform_parsed_article_content import transform_parsed_article_content


runtime = datetime_to_str(get_current_time())


# this should run AFTER load_sources and load_rss_feeds, so it is number 3 in our test order
@pytest.mark.order(3)
def test_extract_article_metadata():
    result: PipelineExecutionResult = execute_pipeline(
        extract_article_metadata,
        mode="local",
        run_config={
            "solids": {
                "get_rss_feeds": {"config": {"sources": ["Reuters"]}},
                "transform_raw_feed_entries_to_articles": {"config": {"runtime": runtime}},
                "load_articles": {"config": {"runtime": runtime}}
            }
        }
    )

    assert result.success


@pytest.mark.order(4)
def test_extract_raw_article_content():
    result: PipelineExecutionResult = execute_pipeline(
        extract_raw_article_content,
        mode="local",
        run_config={
            "solids": {
                "get_articles": {"config": {"begin": runtime, "end": runtime}},
                "request_raw_content": {"config": {"runtime": runtime}},
                "load_raw_content": {"config": {"runtime": runtime}}
            }
        }
    )

    assert result.success


@pytest.mark.order(5)
def test_transform_parsed_article_content():
    result: PipelineExecutionResult = execute_pipeline(
        transform_parsed_article_content,
        mode="local",
        run_config={
            "solids": {
                "get_raw_content": {"config": {"begin": runtime, "end": runtime}},
                "parse_raw_content": {"config": {"runtime": runtime}},
                "load_parsed_content": {"config": {"runtime": runtime}}
            }
        }
    )

    assert result.success


@pytest.mark.order(6)
def test_compute_term_counts():
    result: PipelineExecutionResult = execute_pipeline(
        compute_term_counts,
        mode="local",
        run_config={
            "solids": {
                "get_parsed_content": {"config": {"begin": runtime, "end": runtime}},
                "compute_counts": {"config": {"runtime": runtime}},
                "load_term_counts": {"config": {"runtime": runtime}}
            }
        }
    )

    assert result.success
