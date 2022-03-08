import re
from typing import Union
from unittest.mock import Mock

from bs4 import BeautifulSoup
from dagster import resource


class BaseParser:
    def extract(self, content: str, parse_config: Union[dict, list]) -> str:
        try:
            # dictionary case (our default/common one), treat parse_config as a dictionary with a single configuration
            return self.single_config_extract(content, parse_config)
        except TypeError:
            # list case, a TypeError will be thrown if it isn't a dictionary, so now try to treat it as a list of dict
            for idx, config in enumerate(parse_config):
                try:
                    return self.single_config_extract(content, config)
                except AttributeError as e:
                    # this means that this particular config did not find anything, so try the next one unless it is
                    # the last one
                    if idx + 1 == len(parse_config):
                        raise e

    @staticmethod
    def single_config_extract(content: str, parse_config: dict) -> str:
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
