from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum

import feedparser

from etl.pipelines.html_parsers import BaseParser, url_to_parser


class Lean(Enum):
    LEFT = "LEFT"
    LEAN_LEFT = "LEAN_LEFT"
    CENTER = "CENTER"
    LEAN_RIGHT = "LEAN_RIGHT"
    RIGHT = "RIGHT"


@dataclass
class Feed:
    url: str
    lean: Lean
    content: feedparser.util.FeedParserDict
    title: str = field(init=False)
    html_parser: BaseParser = field(init=False)

    def __post_init__(self):
        self.html_parser = url_to_parser[self.url]
        self.title = self.content.feed.title


@dataclass
class Entry:
    link: str
    summary: str
    title: str


@dataclass
class Article:
    id: str
    feed_url: str
    feed_title: str
    entry: Entry
    content: str

    def __hash__(self):
        return hash(self.id)


Cluster = frozenset[int]
ArticleCluster = frozenset[Article]
Tags = set[str]


@dataclass
class TaggedCluster:
    tags: Tags
    cluster: ArticleCluster


urls_and_leans = [
    # right
    ("https://www.oann.com/category/newsroom/feed", Lean.RIGHT),
    ("http://feeds.feedburner.com/breitbart", Lean.RIGHT),
    ("https://nypost.com/feed/", Lean.RIGHT),
    # ("https://www.dailymail.co.uk/articles.rss", Lean.RIGHT),
    # lean right
    ("http://feeds.foxnews.com/foxnews/latest", Lean.LEAN_RIGHT),
    ("http://feeds.foxnews.com/foxnews/world", Lean.LEAN_RIGHT),
    ("https://www.washingtontimes.com/rss/headlines/news/", Lean.LEAN_RIGHT),
    ("https://www.newsmax.com/rss/Newsfront/16", Lean.LEAN_RIGHT),
    # center
    ("https://feeds.npr.org/1001/rss.xml", Lean.CENTER),
    ("https://feeds.a.dj.com/rss/RSSWorldNews.xml", Lean.CENTER),
    ("https://www.reutersagency.com/feed/?taxonomy=best-regions&post_type=best", Lean.CENTER),
    # ("http://feeds.bbci.co.uk/news/rss.xml", Lean.CENTER),
    # lean left
    ("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", Lean.LEAN_LEFT),
    ("https://www.theguardian.com/world/rss", Lean.LEAN_LEFT),
    # left
    ("https://jacobinmag.com/feed", Lean.LEFT),
    ("https://theintercept.com/feed/?lang=en", Lean.LEFT),
    ("https://www.vox.com/rss/index.xml", Lean.LEFT)
]

headers = OrderedDict([
    ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0"),
    ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"),
    ("Accept-Language", "en-US,en;q=0.5"),
    ("Referer", "https://www.google.com/"),
    ("DNT", "1"),
    ("Connection", "keep-alive"),
    ("Upgrade-Insecure-Requests", "1")
])
