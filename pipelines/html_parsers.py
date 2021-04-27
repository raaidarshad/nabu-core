from abc import abstractmethod

from bs4 import BeautifulSoup


class BaseParser:
    def __init__(self, content: str):
        self.soup = BeautifulSoup(content, "html.parser")

    @abstractmethod
    def extract(self) -> str:
        pass


# right
class OANParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find(class_="entry-content")
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


class BreitbartParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find(class_="entry-content")
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


class NYTPostParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find(class_="entry-content")
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


class DailyMailParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find("div", attrs={"itemprop": "articleBody"})
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


# lean-right
class FoxNewsParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find(class_="article-body")
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


class WashingtonTimesParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find(class_="bigtext")
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


class NewsmaxParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find("div", attrs={"itemprop": "articleBody"})
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


# center
class NPRParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(id="storytext")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


class ReutersParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(class_="et_pb_post_content")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


class WSJParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(class_="article-content")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


# lean-left
class NYTParser(BaseParser):
    def extract(self) -> str:
        story = self.soup.find("section", attrs={"name": "articleBody"})
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


class TheGuardianParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(class_="article-body-commercial-selector")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


# left
class JacobinParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(id="post-content")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


class TheInterceptParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(class_="PostContent")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


class VoxParser(BaseParser):
    def extract(self) -> str:
        storytext = self.soup.find(class_="c-entry-content")
        paragraphs = storytext.find_all("p")
        return " ".join([p.text for p in paragraphs])


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
