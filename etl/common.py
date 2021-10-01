from datetime import datetime, timedelta, timezone
import json
from typing import Union

from dagster.core.execution.context.compute import AbstractComputeExecutionContext
from dateutil import parser
from dateutil.tz import tzutc


Context = AbstractComputeExecutionContext


def get_source_names() -> list[str]:
    with open("db/source.json", "r") as data:
        sources = json.load(data)
        return [s["name"] for s in sources]


def get_current_time() -> datetime:
    return datetime.now(tz=timezone.utc)


def str_to_datetime(target: str) -> datetime:
    parsed = parser.parse(target, tzinfos={"EDT": -14400, "EST": -18000})
    if not parsed.tzinfo:
        parsed = parsed.astimezone(tz=tzutc())
    return parsed


def datetime_to_str(target: datetime) -> str:
    return target.strftime("%Y-%m-%d %H:%M:%S.%f%z")
