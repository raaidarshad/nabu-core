import os
from unittest.mock import MagicMock, Mock

from dagster import resource

import boto3
from botocore.client import BaseClient


@resource
def boto_client(init_context) -> BaseClient:
    session = boto3.session.Session()
    return session.client("s3",
                          region_name=os.getenv("SPACES_REGION", "nyc3"),
                          endpoint_url=os.getenv("SPACES_ENDPOINT", "https://nyc3.digitaloceanspaces.com"),
                          aws_access_key_id=os.getenv("SPACES_KEY"),
                          aws_secret_access_key=os.getenv("SPACES_SECRET"))


@resource
def mock_boto_client() -> BaseClient:
    client = MagicMock(BaseClient)
    client.put_object = Mock(return_value=1)
    return client
