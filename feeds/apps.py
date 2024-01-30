"""Django application configuration for the main feeds app."""

from typing import Literal

from django.apps import AppConfig


class FeedsConfig(AppConfig):
    """Configuration object for the main feeds app.

    Args:
        AppConfig: The base configuration object for Django applications.
    """

    default_auto_field: Literal["django.db.models.BigAutoField"] = "django.db.models.BigAutoField"
    name: Literal["feeds"] = "feeds"
