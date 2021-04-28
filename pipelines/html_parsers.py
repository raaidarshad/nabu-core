from abc import ABCMeta, abstractmethod
from typing import Union

from bs4 import BeautifulSoup, element


class BaseParser(metaclass=ABCMeta):
    def __init__(self, content: str):
        self.soup = BeautifulSoup(content, "html.parser")

    @property
    @abstractmethod
    def target(self) -> dict:
        # this represent the kwargs, as a dict, to pass to the bs4 soup.find method
        pass

    def extract(self) -> str:
        return self.extract_paragraphs(self.extract_story())

    def extract_story(self) -> Union[element.Tag, element.NavigableString]:
        return self.soup.find(**self.target)

    @staticmethod
    def extract_paragraphs(story: Union[element.Tag, element.NavigableString]) -> str:
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


ClassEntryContentParser = type("ClassEntryContentParser", (BaseParser,), {"target": {"class_": "entry-content"}})


# right
class OANParser(ClassEntryContentParser):
    pass


class BreitbartParser(ClassEntryContentParser):
    pass


class NYTPostParser(ClassEntryContentParser):
    pass


class DailyMailParser(BaseParser):
    target = dict(name="div", attrs={"itemprop": "articleBody"})


# lean-right
class FoxNewsParser(BaseParser):
    target = dict(class_="article-body")


class WashingtonTimesParser(BaseParser):
    target = dict(class_="bigtext")


class NewsmaxParser(BaseParser):
    target = dict(name="div", attrs={"itemprop": "articleBody"})


# center
class NPRParser(BaseParser):
    target = dict(id="storytext")


class ReutersParser(BaseParser):
    target = dict(class_="et_pb_post_content")


class WSJParser(BaseParser):
    target = dict(class_="article-content")


# lean-left
class NYTParser(BaseParser):
    target = dict(name="section", attrs={"name": "articleBody"})


class TheGuardianParser(BaseParser):
    target = dict(class_="article-body-commercial-selector")


# left
class JacobinParser(BaseParser):
    target = dict(id="post-content")


class TheInterceptParser(BaseParser):
    target = dict(class_="PostContent")


class VoxParser(BaseParser):
    target = dict(class_="c-entry-content")


url_to_parser = {
    # right
    "https://www.oann.com/category/newsroom/feed": OANParser,
    "http://feeds.feedburner.com/breitbart": BreitbartParser,
    "https://nypost.com/feed/": NYTPostParser,
    "https://www.dailymail.co.uk/articles.rss": DailyMailParser,
    # lean-right
    "http://feeds.foxnews.com/foxnews/latest": FoxNewsParser,
    "http://feeds.foxnews.com/foxnews/world": FoxNewsParser,
    "https://www.washingtontimes.com/rss/headlines/news/": WashingtonTimesParser,
    "https://www.newsmax.com/rss/Newsfront/16": NewsmaxParser,
    # center
    "https://feeds.npr.org/1001/rss.xml": NPRParser,
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml": WSJParser,
    "https://www.reutersagency.com/feed/?taxonomy=best-regions&post_type=best": ReutersParser,
    # "http://feeds.bbci.co.uk/news/rss.xml": BBCWorldParser, SEEMS REALLY HARD TO PARSE
    # lean-left
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml": NYTParser,
    "https://www.theguardian.com/world/rss": TheGuardianParser,
    # TODO wapo, but their feeds aren't working right now
    # left
    "https://jacobinmag.com/feed": JacobinParser,
    "https://theintercept.com/feed/?lang=en": TheInterceptParser,
    "https://www.vox.com/rss/index.xml": VoxParser
}
