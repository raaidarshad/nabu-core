from dagster import repository

from etl.pipelines.compute_clusters import compute_clusters, count_table_day_sensor, count_table_week_sensor
from etl.pipelines.compute_counts import compute_counts, article_table_sensor
from etl.pipelines.extract_articles import extract_articles, main_schedule
from etl.pipelines.load_sources import load_sources


@repository
def ptb_repository():
    return [
        # pipelines
        extract_articles,
        compute_counts,
        compute_clusters,
        load_sources,
        # schedules
        main_schedule,
        # sensors
        article_table_sensor,
        count_table_day_sensor,
        count_table_week_sensor
    ]
