import concurrent.futures
import requests

from dagster import Field, Int, solid

from etl.common import DagsterTime, Context, get_rows_factory, load_rows_factory, str_to_datetime
from ptbmodels.models import Article, RawContent


get_articles = get_rows_factory("get_articles", Article)


MaxWorkers = Field(
    config=Int,
    default_value=10,
    is_required=False
)


@solid(required_resource_keys={"http_client"}, config_schema={"max_workers": MaxWorkers, "runtime": DagsterTime})
def request_raw_content(context: Context, articles: list[Article]) -> list[RawContent]:
    runtime = str_to_datetime(context.solid_config["runtime"])
    http_session: requests.Session = context.resources.http_client

    def _request_and_extract_raw_content(article: Article):
        try:
            # retries and backoff configured in http_client resource, adding a timeout here as well just in case
            response = http_session.get(article.url, timeout=5)
            if response.status_code == 200:
                context.log.info(f"{article.url} requested successfully")
                return RawContent(article_id=article.id, content=response.text, added_at=runtime)
            else:
                context.log.warning(f"Got nonzero status code {response.status_code} for url {article.url}")
        except (requests.HTTPError, requests.exceptions.ConnectionError) as e:
            context.log.warning(f"HTTP error {e} for article with url {article.url} and id {article.id}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=context.solid_config["max_workers"]) as executor:
        raw_content = executor.map(_request_and_extract_raw_content, articles)
    # need to filter out None entries
    return list(filter(None, raw_content))


load_raw_content = load_rows_factory("load_raw_content", RawContent, [RawContent.article_id])
