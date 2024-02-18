from django.apps import AppConfig


class FeedsConfig(AppConfig):
    """This Django app is responsible for managing the feeds."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "feeds"
