import json

from dagster.core.execution.context.compute import AbstractComputeExecutionContext


Context = AbstractComputeExecutionContext


def get_source_names() -> list[str]:
    with open("db/source.json", "r") as data:
        sources = json.load(data)
        return [s["name"] for s in sources]
