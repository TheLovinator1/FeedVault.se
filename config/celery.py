import os
from typing import TYPE_CHECKING

from celery import Celery
from celery import Signature
from celery.app.task import Task
from celery.contrib.abortable import AbortableAsyncResult
from celery.contrib.abortable import AbortableTask
from celery.contrib.django.task import DjangoTask
from celery.local import class_property
from celery.result import AsyncResult
from celery.utils.objects import FallbackContext

if TYPE_CHECKING:
    from config.settings import Any


classes = [
    Celery,
    Task,
    DjangoTask,
    AbortableTask,
    AsyncResult,
    AbortableAsyncResult,
    Signature,
    FallbackContext,
    class_property,
]

for cls in classes:
    setattr(  # noqa: B010
        cls,
        "__class_getitem__",
        classmethod(lambda cls, *args, **kwargs: cls),  # noqa: ARG005
    )

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app: Celery[Task[Any, Any]] = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
