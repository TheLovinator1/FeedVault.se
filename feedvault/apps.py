from typing import TYPE_CHECKING

from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.db.backends.sqlite3.base import DatabaseWrapper
from django.dispatch import receiver

if TYPE_CHECKING:
    from django.db.backends.utils import CursorWrapper


class FeedVaultConfig(AppConfig):
    """FeedVault app configuration."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "feedvault"

    def ready(self) -> None:
        # Make sure the signals are imported so they get used.
        import feedvault.signals  # noqa: F401, PLC0415


@receiver(signal=connection_created)
def activate_wal(sender: DatabaseWrapper, connection: DatabaseWrapper, **kwargs: dict) -> None:  # noqa: ARG001
    """Activate Write-Ahead Logging (WAL) for SQLite databases.

    WAL mode allows for concurrent reads and writes to the database.

    We do this in apps.py because it is the earliest point in the
    application startup process where we can be sure that the database
    connection has been created.

    Args:
        sender: The sender of the signal.
        connection: The connection to the database.
        kwargs: Additional keyword arguments.
    """
    if connection.vendor == "sqlite":
        cursor: CursorWrapper = connection.cursor()
        cursor.execute(sql="PRAGMA journal_mode=WAL;")
