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
        cursor.execute("PRAGMA page_count")
        page_count_result: tuple[int, ...] | None = cursor.fetchone()
        page_count: int | None = page_count_result[0] if page_count_result else None

        db_size: int | None = 4096 * page_count if page_count else None
    return f"{db_size / 1024 / 1024:.2f} MB" if db_size is not None else "0 MB"
