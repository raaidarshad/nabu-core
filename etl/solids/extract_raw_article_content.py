import concurrent.futures
import requests

from dagster import solid
from sqlmodel import Session, select

from etl.common import DagsterTime, Context, load_rows_factory, str_to_datetime
from ptbmodels.models import Article, RawContent


@solid(required_resource_keys={"database_client"}, config_schema={"begin": DagsterTime, "end": DagsterTime})
def get_articles(context: Context) -> list[Article]:
    db_client: Session = context.resources.database_client
    begin = str_to_datetime(context.solid_config["begin"])
    end = str_to_datetime(context.solid_config["end"])

    statement = select(Article).where((begin <= Article.added_at) & (Article.added_at <= end))
    context.log.debug(f"Attempting to execute: {statement}")
    articles = db_client.exec(statement).all()
    context.log.debug(f"Got {len(articles)} articles")
    return articles


@solid(required_resource_keys={"http_client"})
def request_raw_content(context: Context, articles: list[Article]) -> RawContent:
    ...


load_raw_content = load_rows_factory("load_raw_content", RawContent, ["article_id"])
