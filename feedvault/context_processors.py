from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def add_global_context(request: HttpRequest) -> dict[str, str | int]:
    """Add global context to all templates.

    Args:
        request: The request object.

    Returns:
        A dictionary with the global context.
    """
    from feedvault.stats import get_db_size  # noqa: PLC0415

    from .models import Feed  # noqa: PLC0415

    db_size: str = get_db_size()
    amount_of_feeds: int = Feed.objects.count()
    return {
        "db_size": db_size,
        "amount_of_feeds": amount_of_feeds,
    }
