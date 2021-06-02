from dagster import repository

from etl.pipelines.extract_articles import extract_articles, main_schedule


@repository
def ptb_repository():
    return [extract_articles, main_schedule]
