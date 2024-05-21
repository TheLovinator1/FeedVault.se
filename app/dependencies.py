"""https://fastapi.tiangolo.com/tutorial/dependencies/."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

import humanize
from fastapi import Depends
from reader import EntryCounts, FeedCounts, Reader, make_reader

from app.settings import DB_PATH


@lru_cache(maxsize=1)
def get_reader() -> Reader:
    """Return the reader."""
    return make_reader(url=DB_PATH.as_posix(), search_enabled=True)


def get_stats() -> str:
    """Return the stats."""
    db_size: int = DB_PATH.stat().st_size

    # Get the feed counts.
    feed_counts: FeedCounts = get_reader().get_feed_counts()
    total_feed_counts: int | None = feed_counts.total
    if total_feed_counts is None:
        total_feed_counts = 0

    # Get the entry counts.
    entry_counts: EntryCounts = get_reader().get_entry_counts()
    total_entry_counts: int | None = entry_counts.total
    if total_entry_counts is None:
        total_entry_counts = 0

    return f"{total_feed_counts} feeds ({total_entry_counts} entries) ~{humanize.naturalsize(db_size, binary=True)}"


CommonReader = Annotated[Reader, Depends(get_reader)]
CommonStats = Annotated[str, Depends(get_stats)]
