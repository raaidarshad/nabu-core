from unittest.mock import Mock

from dagster import resource
import feedparser


class RssParser:
    @staticmethod
    def parse(*args, **kwargs):
        return feedparser.parse(*args, **kwargs)


@resource
def rss_parser() -> RssParser:
    return RssParser()


@resource
def mock_rss_parser() -> RssParser:
    return Mock(spec=RssParser)
