import json

from dagster import AssetMaterialization, Output, String, solid
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, SQLModel

from etl.common import Context
from ptbmodels.models import RssFeed, Source


def get_entities_from_file_factory(name: str, entity_type, **kwargs):
    @solid(name=name, **kwargs)
    def _load_rows_solid(context: Context, path_format: str):
        context.log.debug(f"Loading {entity_type.__name__} from JSON file")
        # load entities
        entities = _load_json(filepath=path_format.format(table_name=entity_type.__tablename__))
        # emit entities
        # entities = [entity_type(**e) for e in j_entities]
        return entities
    return _load_rows_solid


get_sources_from_file = get_entities_from_file_factory("get_sources_from_file", Source)
get_rss_feeds_from_file = get_entities_from_file_factory("get_rssfeeds_from_file", RssFeed)


@solid(required_resource_keys={"database_engine"}, config_schema={"path": String})
def create_tables(context: Context) -> str:
    path = context.solid_config["path"]
    db_engine = context.resources.database_engine
    SQLModel.metadata.create_all(db_engine)
    return path + "/{table_name}.json"


def load_rows_factory(name: str, entity_type, on_conflict_col: str, **kwargs):
    @solid(name=name, required_resource_keys={"database_client"}, **kwargs)
    def _load_rows_solid(context: Context, entities: list):
        # get db session
        db_client: Session = context.resources.database_client

        context.log.debug(f"Attempting to add {len(entities)} rows to the {entity_type.__name__} table")
        count_before = db_client.query(entity_type).count()
        insert_statement = insert(entity_type).on_conflict_do_nothing(index_elements=[on_conflict_col])
        db_client.exec(statement=insert_statement, params=entities)
        db_client.commit()
        count_after = db_client.query(entity_type).count()
        added = count_after - count_before
        context.log.debug(f"Added {added} rows to the {entity_type.__name__} table")

        if added > 0:
            yield AssetMaterialization(
                asset_key=f"{entity_type.__tablename__}_table",
                description=f"New rows added to {entity_type.__tablename__} table"
            )
        yield Output(entities)

    return _load_rows_solid


load_source_rows = load_rows_factory("load_source_rows", Source, "name")
load_rss_feed_rows = load_rows_factory("load_rss_feed_rows", RssFeed, "url")


def _load_json(filepath: str) -> list[dict]:
    with open(filepath, "r") as data:
        return json.load(data)
