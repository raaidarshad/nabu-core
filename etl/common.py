from datetime import datetime, timezone
import json
import os
import re
from typing import Type
import unicodedata

from dagster.core.execution.context.compute import AbstractComputeExecutionContext
from dagster import AssetMaterialization, Field, Output, String, solid
from dateutil import parser
from dateutil.tz import tzutc
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select


from ptbmodels.models import PTBModel, PTBTagModel

Context = AbstractComputeExecutionContext
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def clean_text(dirty: str) -> str:
    return unicodedata.normalize("NFKD", re.sub(CLEANR, '', dirty))


def get_source_names() -> list[str]:
    path = os.getenv("DB_PATH", "etl/db")
    with open(f"{path}/source.json", "r") as data:
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


DagsterTime = Field(
    config=String,
    default_value=datetime_to_str(get_current_time()),
    is_required=False
)


# TODO will likely add config to filter by source, and perhaps a "by id" override filter
def get_rows_factory(name: str, entity_type: Type[PTBTagModel], **kwargs):
    @solid(name=name,
           required_resource_keys={"database_client"},
           config_schema={"begin": DagsterTime, "end": DagsterTime}, **kwargs)
    def _get_rows_solid(context: Context):
        db_client: Session = context.resources.database_client
        begin = str_to_datetime(context.solid_config["begin"])
        end = str_to_datetime(context.solid_config["end"])

        statement = select(entity_type).where((begin <= entity_type.added_at) & (entity_type.added_at <= end))
        context.log.debug(f"Attempting to execute: {statement}")
        entities = db_client.exec(statement).all()
        context.log.debug(f"Got {len(entities)} rows of {entity_type.__name__}")
        return entities
    return _get_rows_solid


def load_rows_factory(name: str, entity_type: Type[PTBModel], on_conflict: list, do_update: bool = False, **kwargs):
    @solid(name=name, required_resource_keys={"database_client"}, config_schema={"runtime": DagsterTime},  **kwargs)
    def _load_rows_solid(context: Context, entities: list[PTBModel]):
        # get db session
        db_client: Session = context.resources.database_client

        if entities:
            context.log.debug(f"Attempting to add {len(entities)} rows to the {entity_type.__name__} table")
            count_before = db_client.query(entity_type).count()
            base_insert_statement = insert(entity_type)
            if do_update:
                # TODO not sure how to make this generalized for the set_ argument
                insert_statement = base_insert_statement.on_conflict_do_update(
                    index_elements=on_conflict,
                    set_=dict(base_insert_statement.excluded)
                )
            else:
                insert_statement = insert(entity_type).on_conflict_do_nothing(index_elements=on_conflict)
            db_client.exec(statement=insert_statement, params=[e.dict() for e in entities])
            db_client.commit()
            count_after = db_client.query(entity_type).count()
            added = count_after - count_before
            context.log.debug(f"Added {added} rows to the {entity_type.__name__} table")

            if added > 0:
                yield AssetMaterialization(
                    asset_key=f"{entity_type.__tablename__}_table",
                    description=f"New rows added to {entity_type.__tablename__} table",
                    tags={"runtime": context.solid_config["runtime"]}
                )
            yield Output(entities)
        else:
            context.log.debug("No entities to add")
            yield Output(entities)

    return _load_rows_solid
