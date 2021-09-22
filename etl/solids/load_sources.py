import os
import json

from dagster import AssetMaterialization, Output, solid
from sqlmodel import Session, SQLModel

from etl.common import Context
from etl.models import Source


@solid(required_resource_keys={"database_client"})
def load_sources_from_file(context: Context, filepath: str):
    # get db session
    db_client: Session = context.resources.database_client
    # load json file
    raw_sources = _load_json(filepath=filepath)
    # write to db
    sources = [Source(**src) for src in raw_sources]
    _write_sources(db=db_client, sources=sources)
    yield AssetMaterialization(
        asset_key="source_table",
        description="Initial rows added to source table, from file"
    )
    yield Output(sources)


@solid(required_resource_keys={"database_engine"})
def create_tables(context: Context) -> str:
    db_engine = context.resources.database_engine
    SQLModel.metadata.create_all(db_engine)
    return "etl/db/sources.json"


def _load_json(filepath: str) -> list[dict]:
    with open(filepath, "r") as data:
        return json.load(data)


def _write_sources(db: Session, sources: list[Source]):
    db.add_all(sources)
    db.commit()
