from dagster import repository

from etl.pipelines.compute_article_clusters import compute_article_clusters, article_cluster_schedule_12h,\
    article_cluster_schedule_1d, article_cluster_schedule_3d, compute_article_clusters_sensor
from etl.pipelines.compute_term_counts import compute_term_counts, compute_counts_sensor
from etl.pipelines.extract_article_metadata import extract_article_metadata, main_schedule
from etl.pipelines.transform_parsed_article_content import transform_parsed_article_content,\
    transform_parsed_article_content_sensor
from etl.pipelines.extract_raw_article_content import extract_raw_article_content, extract_raw_article_content_sensor
from etl.pipelines.load_sources import load_biases, load_rss_feeds, load_sources
from etl.pipelines.write_latest_clusters import write_latest_clusters, write_latest_clusters_sensor


@repository
def ptb_repository():
    return [
        # pipelines
        compute_article_clusters,
        compute_term_counts,
        extract_article_metadata,
        extract_raw_article_content,
        transform_parsed_article_content,
        load_biases,
        load_sources,
        load_rss_feeds,
        write_latest_clusters,
        # schedules
        main_schedule,
        article_cluster_schedule_12h,
        article_cluster_schedule_1d,
        article_cluster_schedule_3d,
        # sensors
        compute_article_clusters_sensor,
        extract_raw_article_content_sensor,
        transform_parsed_article_content_sensor,
        compute_counts_sensor,
        write_latest_clusters_sensor
    ]
