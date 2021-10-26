from dagster import repository

from etl.pipelines.compute_article_clusters import compute_article_clusters, measure_clustering_methods
from etl.pipelines.compute_term_counts import compute_term_counts, compute_counts_sensor
from etl.pipelines.extract_article_metadata import extract_article_metadata, main_schedule
from etl.pipelines.transform_parsed_article_content import transform_parsed_article_content,\
    transform_parsed_article_content_sensor
from etl.pipelines.extract_raw_article_content import extract_raw_article_content, extract_raw_article_content_sensor
from etl.pipelines.load_sources import load_rss_feeds, load_sources


@repository
def ptb_repository():
    return [
        # pipelines
        compute_article_clusters,
        compute_term_counts,
        extract_article_metadata,
        extract_raw_article_content,
        measure_clustering_methods,
        transform_parsed_article_content,
        load_sources,
        load_rss_feeds,
        # schedules
        main_schedule,
        # sensors
        extract_raw_article_content_sensor,
        transform_parsed_article_content_sensor,
        compute_counts_sensor
    ]
