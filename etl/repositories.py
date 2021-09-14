from dagster import repository

from etl.pipelines.compute_clusters import compute_clusters
from etl.pipelines.compute_counts import compute_counts
from etl.pipelines.extract_articles import extract_articles, main_schedule


@repository
def ptb_repository():
    return [extract_articles, main_schedule, compute_counts, compute_clusters]
