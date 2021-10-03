from dagster import String, solid

from etl.common import DagsterTime, Context
from ptbmodels.models import Article, RawContent

@solid(required_resource_keys={"database_client"}, config_schema={"begin": DagsterTime, "end": DagsterTime})
def get_articles(context: Context) -> list[Article]:
    ...


@solid(required_resource_keys={"http_client"})
def request_raw_content(context: Context, articles: list[Article]) -> RawContent:
    ...


@solid(required_resource_keys={"database_client"}, config_schema={"runtime": DagsterTime})
def load_raw_content(context: Context, raw_content: list[RawContent]):
    ...