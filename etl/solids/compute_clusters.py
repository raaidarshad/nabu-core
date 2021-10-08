from dagster import AssetMaterialization, Float, Int, Output, solid
from datetime import datetime, timedelta, timezone
from sqlmodel import Session

from etl.common import Context
from etl.functions.counts import CountData, get_count_data
from etl.functions.tfidf import SimilarityData, compute_similarity_data
from etl.functions.clusters import compute_cluster_data


# want to do this with various clustering methods; do we want to store similarity data as
# an intermediate piece? or we can wrap various clustering methods into solids,
# then create specific pipelines and configs. needs some thinking/writing

# get count terms
# compute similarity
# compute article clusters
# load article clusters


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


@solid(required_resource_keys={"database_client"}, config_schema={"minute_span": Int})
def compute_and_load_clusters(context: Context, similarity_data: SimilarityData):
    minute_span = context.solid_config["minute_span"]
    db_client: Session = context.resources.database_client
    compute_cluster_data(similarity_data, datetime.now(tz=timezone.utc), minute_span, db_client)
    yield AssetMaterialization(asset_key="cluster_table", description="New rows added to cluster table")
    # yield a dummy output, don't have access to the rows to add right here
    yield Output(1)
