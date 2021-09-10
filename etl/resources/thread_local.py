import threading
from unittest.mock import Mock

from dagster import resource


@resource
def thread_local():
    return threading.local()


@resource
def mock_thread_local():
    return Mock(spec=threading.local)
