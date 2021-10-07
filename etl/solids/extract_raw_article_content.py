import concurrent.futures
import requests

from dagster import Field, Int, solid
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


MaxWorkers = Field(
    config=Int,
    default_value=10,
    is_required=False
)


@solid(required_resource_keys={"http_client"}, config_schema={"max_workers": MaxWorkers, "runtime": DagsterTime})
def request_raw_content(context: Context, articles: list[Article]) -> list[RawContent]:
    runtime = str_to_datetime(context.solid_config["runtime"])

    def _request_and_extract_raw_content(article: Article):
        http_session: requests.Session = context.resources.http_client
        try:
            response = http_session.get(article.url)
            if response.status_code == 200:
                return RawContent(article_id=article.id, content=response.text, added_at=runtime)
            else:
                context.log.warning(f"Got nonzero status code {response.status_code} for url {article.url}")
        except requests.HTTPError as e:
            context.log.warning(f"HTTP error {e} for article with url {article.url} and id {article.id}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=context.solid_config["max_workers"]) as executor:
        raw_content = executor.map(_request_and_extract_raw_content, articles)
    # need to filter out None entries
    return list(filter(None, raw_content))


load_raw_content = load_rows_factory("load_raw_content", RawContent, ["article_id"])
