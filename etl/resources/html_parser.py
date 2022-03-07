import re
from unittest.mock import Mock

from bs4 import BeautifulSoup
from dagster import resource


class BaseParser:
    @staticmethod
    def extract(content: str, parse_config: dict) -> str:
        # TODO change this so that it considers the possibility that parse_config is a list of possible configs
        soup = BeautifulSoup(content, "html.parser")
        # check if there is a regex config
        try:
            # if there is a key of "regex" and the value is "true",
            # pass the parse_config values as regex
            regex_arg = parse_config.pop("regex")
            if regex_arg:
                for item in parse_config.items():
                    parse_config.update({item[0]: re.compile(item[1])})
        except KeyError:
            # there is no regex config, so there is nothing extra to do
            pass
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
