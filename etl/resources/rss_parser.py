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
    rp = Mock(spec=RssParser)
    rp.parse = Mock(return_value=feedparser.FeedParserDict({
        "status": 200,
        "feed": {"updated": str(datetime.now(timezone.utc)),
                 "link": "https://www.fake.com",
                 "title": "myfeed_title",
                 "subtitle": "myfeed_subtitle"
                 },
        "entries": [feedparser.FeedParserDict(
            {"title": "fake_title",
             "summary": "fake_summary",
             "published": str(datetime.now(timezone.utc)),
             "link": "https://www.fake.com",
             "author": "pencil mcpen"
             })]
    }))
    return rp
