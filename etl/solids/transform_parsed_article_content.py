from dagster import solid

from etl.common import DagsterTime, Context, get_rows_factory, load_rows_factory, str_to_datetime
from etl.resources.html_parser import BaseParser
from ptbmodels.models import ParsedContent, RawContent

get_raw_content = get_rows_factory("get_raw_content", RawContent)


@solid(required_resource_keys={"html_parser"}, config_schema={"runtime": DagsterTime})
def parse_raw_content(context: Context, raw_content: list[RawContent]) -> list[ParsedContent]:
    runtime = str_to_datetime(context.solid_config["runtime"])
    parser: BaseParser = context.resources.html_parser
    return [ParsedContent(
        article_id=raw.article_id,
        # don't think this will work since we're not in the same scope as when we pull the rows
        # the first time; if it does, great! if it doesn't, can intentionally join to get data
        content=parser.extract(raw.content, raw.article.rss_feed.parser_config),
        added_at=runtime)
        for raw in raw_content]


load_parsed_content = load_rows_factory("load_parsed_content",
                                        ParsedContent,
                                        [ParsedContent.article_id])