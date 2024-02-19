from __future__ import annotations

import logging

from django.core.cache import cache
from django.db import connection

logger: logging.Logger = logging.getLogger(__name__)


def get_db_size() -> str:
    """Get the size of the database.

    Returns:
        str: The size of the database.
    """
    # Try to get value from cache
    db_size = cache.get("db_size")

    if db_size is not None:
        logger.debug("Got db_size from cache")
        return db_size

    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        row = cursor.fetchone()

    db_size = "0 MB" if row is None else str(row[0])

    # Store value in cache for 15 minutes
    cache.set("db_size", db_size, 60 * 15)

    return db_size
