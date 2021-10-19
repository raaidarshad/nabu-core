from dagster import solid

from etl.common import DagsterTime, Context, get_rows_factory, load_rows_factory, str_to_datetime
from etl.resources.html_parser import BaseParser
from ptbmodels.models import ParsedContent, RawContent

get_raw_content = get_rows_factory("get_raw_content", RawContent)


@solid(required_resource_keys={"html_parser"}, config_schema={"runtime": DagsterTime})
def parse_raw_content(context: Context, raw_content: list[RawContent]) -> list[ParsedContent]:
    runtime = str_to_datetime(context.solid_config["runtime"])
    parser: BaseParser = context.resources.html_parser

    def _raw_to_parsed(raw: RawContent):
        try:
            return ParsedContent(
                article_id=raw.article_id,
                content=parser.extract(raw.content, raw.article.rss_feed.parser_config),
                added_at=runtime)
        except AttributeError:
            context.log.debug(
                f"Article id {raw.article_id} with parser_config {raw.article.rss_feed.parser_config} failed to parse.")

    # filter out None values for when we have a try/except statement implemented
    return list(filter(None, [_raw_to_parsed(raw) for raw in raw_content]))


load_parsed_content = load_rows_factory("load_parsed_content",
                                        ParsedContent,
                                        [ParsedContent.article_id])
