from dagster import resource
import feedparser


class RssParser:
    @staticmethod
    def parse(**kwargs):
        return feedparser.parse(**kwargs)


@resource
def rss_parser(_init_context) -> RssParser:
    return RssParser()

