import boto3
from dagster import resource


@resource
def boto_client(init_context):
    session = boto3.Session()
    client = session.client(
        region_name="",
        endpoint_url="",
        aws_access_key_id="",
        aws_secret_access_key=""
    )
