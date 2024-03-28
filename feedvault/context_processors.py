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
    from .models import Feed  # noqa: PLC0415

    amount_of_feeds: int = Feed.objects.count()
    return {"amount_of_feeds": amount_of_feeds}
