import yaml

from dagster.core.execution.context.compute import AbstractComputeExecutionContext


Context = AbstractComputeExecutionContext


def load_config(filepath: str) -> dict:
    """
    Utility to load pipeline configs from YAML files
    :param filepath: file path as a string to the target configuration
    :return: dict representation of config
    """
    with open(filepath) as raw_config:
        return yaml.load(raw_config)
