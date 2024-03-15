from __future__ import annotations

import logging

from django.db import connection

logger: logging.Logger = logging.getLogger(__name__)


def get_db_size() -> str:
    """Get the size of the database.

    Returns:
        str: The size of the database.
    """
    # Get SQLite database size
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA page_size")
        page_size_result = cursor.fetchone()
        page_size = page_size_result[0] if page_size_result else None

        cursor.execute("PRAGMA page_count")
        page_count_result = cursor.fetchone()
        page_count = page_count_result[0] if page_count_result else None

        db_size = page_size * page_count if page_size and page_count else None
    return f"{db_size / 1024 / 1024:.2f} MB" if db_size is not None else "0 MB"
