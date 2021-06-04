from datetime import datetime, timezone
from unittest.mock import Mock

from dagster import resource
import feedparser


class RssParser:
    @staticmethod
    def parse(*args, **kwargs):
        return feedparser.parse(*args, **kwargs)


@resource
def rss_parser(_init_context) -> RssParser:
    return RssParser()


@resource
def test_rss_parser(_init_context) -> RssParser:
    return Mock(spec=RssParser)
