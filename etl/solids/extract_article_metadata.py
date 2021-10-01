from dagster import Array, AssetMaterialization, Enum, EnumValue, Field, Output, String, solid

from sqlmodel import Session, select

from etl.common import Context, get_source_names
from ptbmodels.models import Source

SourceDenum = Enum("SourceDenum", [EnumValue("all")] + [EnumValue(n) for n in get_source_names()])

SourceDenumConfig = Field(
    config=Array(SourceDenum),
    default_value=["all"],
    is_required=False
)


@solid(required_resource_keys={"database_client"},
       config_schema={"sources": SourceDenumConfig})
def get_sources(context: Context) -> list[Source]:
    db_client: Session = context.resources.database_client
    source_names = context.solid_config["sources"]
    if "all" in source_names:
        statement = select(Source)
    else:
        statement = select(Source).where(Source.name.in_(source_names))
    context.log.debug(f"Attempting to execute: {statement}")
    sources = db_client.exec(statement).all()
    context.log.debug(f"Got {len(sources)} sources")
    return sources
