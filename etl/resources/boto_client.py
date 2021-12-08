import os
from unittest.mock import MagicMock

from dagster import resource

import boto3
from botocore.client import BaseClient


@resource
def boto_client(init_context) -> BaseClient:
    session = boto3.session.Session()
    return session.client('s3',
                          region_name='nyc3',
                          endpoint_url='https://nyc3.digitaloceanspaces.com',
                          aws_access_key_id=os.getenv('SPACES_KEY'),
                          aws_secret_access_key=os.getenv('SPACES_SECRET'))


def mock_boto_client(init_context) -> BaseClient:
    return MagicMock(BaseClient)
