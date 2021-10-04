from dagster import repository
#
# from etl.pipelines.compute_clusters import compute_clusters, count_table_day_sensor, count_table_week_sensor
# from etl.pipelines.compute_counts import compute_counts, article_table_sensor
# from etl.pipelines.extract_articles import extract_articles, main_schedule
from etl.pipelines.extract_article_metadata import extract_article_metadata
from etl.pipelines.extract_raw_article_content import extract_raw_article_content
from etl.pipelines.load_sources import load_rss_feeds, load_sources


@repository
def ptb_repository():
    return [
        # pipelines
        # extract_articles,
        # compute_counts,
        # compute_clusters,
        extract_article_metadata,
        extract_raw_article_content,
        load_sources,
        load_rss_feeds,
        # schedules
        # main_schedule,
        # sensors
        # article_table_sensor,
        # count_table_day_sensor,
        # count_table_week_sensor
    ]
