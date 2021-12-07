from dagster import solid
from sqlmodel import Session, func, select

from etl.common import Context
from ptbmodels.models import ArticleCluster


@solid(required_resource_keys={"database_client"})
def get_latest_article_clusters(context: Context):
    db_client: Session = context.resources.database_client

    inner_statement = select(func.max(ArticleCluster.added_at)).scalar_subquery()
    statement = select(ArticleCluster).where(ArticleCluster.added_at == inner_statement)
    context.log.info(f"Attempting to execute: {statement}")
    entities = db_client.exec(statement).all()
    context.log.info(f"Got {len(entities)} rows of {ArticleCluster.__name__}")
    return entities
