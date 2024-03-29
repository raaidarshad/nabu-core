import json

from botocore.client import BaseClient
from dagster import Field, Int, String, solid
from sqlmodel import Session, column, desc, distinct, func, select

from etl.common import Context, datetime_to_str, format_cluster_range
from ptbmodels.models import Article, ArticleCluster, ArticleClusterLink, Source

ClusterLimit = Field(config=Int, default_value=10, is_required=False)


@solid(required_resource_keys={"database_client"},
       config_schema={"cluster_limit": ClusterLimit, "cluster_range": Field(config=dict, is_required=True)})
def get_latest_clusters(context: Context):
    db_client: Session = context.resources.database_client
    cluster_range = context.solid_config["cluster_range"]
    formatted_cluster_range = format_cluster_range(cluster_range)
    context.log.debug(f"Raw cluster range is: {cluster_range}")
    context.log.debug(f"Formatted cluster range is: {formatted_cluster_range}")

    statement1 = select(
        ArticleClusterLink.article_cluster_id,
        func.count(distinct(Source.id)).label("size")). \
        join(Article, Article.id == ArticleClusterLink.article_id). \
        join(Source, Source.id == Article.source_id). \
        group_by(ArticleClusterLink.article_cluster_id). \
        order_by(desc("size"))
    sub1 = statement1.subquery("s1")
    sub2 = select(func.max(ArticleCluster.added_at)).\
        where(ArticleCluster.end - ArticleCluster.begin == formatted_cluster_range).scalar_subquery()
    statement2 = select(ArticleCluster, column("size")).join(sub1).\
        where(ArticleCluster.added_at == sub2).\
        where(ArticleCluster.end - ArticleCluster.begin == formatted_cluster_range).\
        order_by(desc("size")).limit(context.solid_config["cluster_limit"])

    context.log.info(f"Attempting to execute: {statement2}")
    entities = db_client.exec(statement2).all()
    context.log.info(f"Got {len(entities)} rows of {ArticleCluster.__name__}")
    return entities


@solid
def prep_latest_clusters(context: Context, clusters) -> dict:
    prepped_clusters = [
        {
            "topics": [{"term": k.term, "weight": k.weight} for k in c[0].keywords],
            "articles": [
                {"title": a.title, "url": a.url, "source": a.source.name, "date": a.published_at.strftime("%d-%m-%Y")}
                for a in sorted(c[0].articles, key=lambda item: item.published_at, reverse=True)],
            "source_count": c[1]
        }
        for c in clusters
    ]

    return {
        "added_at": datetime_to_str(clusters[0][0].added_at),
        "clusters": prepped_clusters
    }


@solid(required_resource_keys={"boto_client"}, config_schema={"bucket": String, "key": String})
def write_to_bucket(context: Context, prepped_data: dict):
    boto_client: BaseClient = context.resources.boto_client

    boto_client.put_object(
        Bucket=context.solid_config["bucket"],
        Key=context.solid_config["key"],
        Body=json.dumps(prepped_data),
        ACL="public-read"
    )
