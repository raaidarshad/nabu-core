import threading
from unittest.mock import Mock

from dagster import resource


@resource
def thread_local(_init_context):
    return threading.local()


@resource
def test_thread_local(_init_context):
    return Mock(spec=threading.local)
