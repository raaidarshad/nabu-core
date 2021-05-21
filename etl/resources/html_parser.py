from bs4 import BeautifulSoup
from dagster import resource


class BaseParser:
    @staticmethod
    def extract(content: bytes, parse_config: dict) -> str:
        soup = BeautifulSoup(content, "html.parser")
        story = soup.find(**parse_config)
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


@resource
def html_parser(_init_context) -> BaseParser:
    return BaseParser()
