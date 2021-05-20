from enum import Enum
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


class MbfcBias(Enum):
    LEAST_BIASED = "LEAST_BIASED"
    LEFT_CENTER = "LEFT_CENTER"
    RIGHT_CENTER = "RIGHT_CENTER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FAR_LEFT = "FAR_LEFT"
    FAR_RIGHT = "FAR_RIGHT"


class MbfcAccuracy(Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MIXED = "MIXED"
    MOSTLY_FACTUAL = "MOSTLY_FACTUAL"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class AfBias(Enum):
    MIDDLE = "MIDDLE"
    SKEWS_LEFT = "SKEWS_LEFT"
    SKEWS_RIGHT = "SKEWS_RIGHT"
    HYPER_PARTISAN_LEFT = "HYPER_PARTISAN_LEFT"
    HYPER_PARTISAN_RIGHT = "HYPER_PARTISAN_RIGHT"
    MOST_EXTREME_LEFT = "MOST_EXTREME_LEFT"
    MOST_EXTREME_RIGHT = "MOST_EXTREME_RIGHT"


class AfAccuracy(Enum):
    pass


class AsBias(Enum):
    LEFT = "LEFT"
    LEAN_LEFT = "LEAN_LEFT"
    CENTER = "CENTER"
    LEAN_RIGHT = "LEAN_RIGHT"
    RIGHT = "RIGHT"
