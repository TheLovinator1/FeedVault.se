from django.apps import AppConfig


class FeedVaultConfig(AppConfig):
    """FeedVault app configuration."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "feedvault"
