from dagster import String, solid
from sqlmodel import SQLModel

from etl.common import Context, load_json, load_rows_factory
from ptbmodels.models import RssFeed, Source


def get_entities_from_file_factory(name: str, entity_type, **kwargs):
    @solid(name=name, **kwargs)
    def _load_rows_solid(context: Context, path_format: str):
        context.log.info(f"Loading {entity_type.__name__} from JSON file")
        # load entities
        j_entities = load_json(filepath=path_format.format(table_name=entity_type.__tablename__))
        # emit entities
        entities = [entity_type(**e) for e in j_entities]
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


load_source_rows = load_rows_factory("load_source_rows", Source, [Source.name])
load_rss_feed_rows = load_rows_factory("load_rss_feed_rows", RssFeed, [RssFeed.url])
