from unittest.mock import Mock

from bs4 import BeautifulSoup
from dagster import resource


class BaseParser:
    @staticmethod
    def extract(content: str, parse_config: dict) -> str:
        soup = BeautifulSoup(content, "html.parser")
        story = soup.find(**parse_config)
        paragraphs = story.find_all("p")
        return " ".join([p.text for p in paragraphs])


@resource
def html_parser() -> BaseParser:
    return BaseParser()


@resource
def mock_html_parser() -> BaseParser:
    bp = Mock(spec=BaseParser)
    bp.extract = Mock(return_value="fake joined text")
    return bp
