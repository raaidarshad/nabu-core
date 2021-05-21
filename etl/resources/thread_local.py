import threading

from dagster import resource


@resource
def thread_local(_init_context):
    return threading.local()
