from dagster import Float, Int, solid
from datetime import datetime, timedelta, timezone
from sqlmodel import Session

from etl.common import Context
from etl.functions.counts import CountData, get_count_data
from etl.functions.tfidf import SimilarityData, compute_similarity_data
from etl.functions.clusters import compute_cluster_data, load_clusters
from etl.models import Cluster


# TODO these all need tests
@solid(required_resource_keys={"database_client"}, config_schema={"minute_span": Int})
def get_counts(context: Context) -> CountData:
    db_client: Session = context.resources.database_client
    minute_span = context.solid_config["minute_span"]
    now = datetime.now(tz=timezone.utc)
    threshold = now - timedelta(minutes=minute_span)
    return get_count_data(datetime_threshold=threshold, db_client=db_client)


@solid(config_schema={"filter_threshold": Float})
def compute_similarity(context: Context, count_data: CountData) -> SimilarityData:
    filter_threshold = context.solid_config["filter_threshold"]
    return compute_similarity_data(count_data=count_data, filter_threshold=filter_threshold)


@solid(config_schema={"minute_span": Int})
def compute_clusters(context: Context, similarity_data: SimilarityData) -> list[Cluster]:
    minute_span = context.solid_config["minute_span"]
    return compute_cluster_data(similarity_data, datetime.now(tz=timezone.utc), minute_span)


@solid(required_resource_keys={"database_client"})
def load_clusters(context: Context, clusters: list[Cluster]):
    db_client: Session = context.resources.database_client
    load_clusters(clusters, db_client)
