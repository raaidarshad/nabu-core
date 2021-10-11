import threading
from unittest.mock import MagicMock

from dagster import resource


@resource
def thread_local():
    return threading.local()


@resource
def mock_thread_local():
    return MagicMock(spec=threading.local)
