from __future__ import annotations

import logging

from django.db import connection

logger: logging.Logger = logging.getLogger(__name__)


def get_db_size() -> str:
    """Get the size of the database.

    Returns:
        str: The size of the database.
    """
    # Get Postgres database size
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        db_size_result: tuple[str, ...] | None = cursor.fetchone()
        db_size: str | None = db_size_result[0] if db_size_result else None

    return db_size if db_size is not None else "0 MB"
