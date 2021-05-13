from bs4 import BeautifulSoup


class BaseParser:
    def __init__(self, target: dict):
        self.target = target

    def extract(self, content: bytes) -> str:
        soup = BeautifulSoup(content, "html.parser")
        story = soup.find(**self.target)
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


url_to_parser = {
    # right
    "https://www.oann.com/category/newsroom/feed": BaseParser(target=dict(class_="entry-content")),
    "http://feeds.feedburner.com/breitbart": BaseParser(target=dict(class_="entry-content")),
    "https://nypost.com/feed/": BaseParser(target=dict(class_="entry-content")),
    "https://www.dailymail.co.uk/articles.rss": BaseParser(target=dict(name="div", attrs={"itemprop": "articleBody"})),
    # lean-right
    "http://feeds.foxnews.com/foxnews/latest": BaseParser(target=dict(class_="article-body")),
    "http://feeds.foxnews.com/foxnews/world": BaseParser(target=dict(class_="article-body")),
    "https://www.washingtontimes.com/rss/headlines/news/": BaseParser(target=dict(class_="bigtext")),
    "https://www.newsmax.com/rss/Newsfront/16": BaseParser(target=dict(name="div", attrs={"itemprop": "articleBody"})),
    # center
    "https://feeds.npr.org/1001/rss.xml": BaseParser(target=dict(id="storytext")),
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml": BaseParser(target=dict(class_="article-content")),
    "https://www.reutersagency.com/feed/?taxonomy=best-regions&post_type=best": BaseParser(
        target=dict(class_="et_pb_post_content")),
    # "http://feeds.bbci.co.uk/news/rss.xml": BBCWorldParser, SEEMS REALLY HARD TO PARSE
    # lean-left
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml": BaseParser(
        target=dict(name="section", attrs={"name": "articleBody"})),
    "https://www.theguardian.com/world/rss": BaseParser(target=dict(class_="article-body-commercial-selector")),
    # TODO wapo, but their feeds aren't working right now
    # left
    "https://jacobinmag.com/feed": BaseParser(target=dict(id="post-content")),
    "https://theintercept.com/feed/?lang=en": BaseParser(target=dict(class_="PostContent")),
    "https://www.vox.com/rss/index.xml": BaseParser(target=dict(class_="c-entry-content"))
}
