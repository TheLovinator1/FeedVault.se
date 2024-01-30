"""Views for the feeds app.

/ - Index page

"""

from __future__ import annotations

from django.db import connection
from django.views.generic.base import TemplateView

from feeds.models import Feed


def get_database_size() -> int:
    """Get the size of a database.

    Returns:
        The size of the database in megabytes.
    """
    with connection.cursor() as cursor:
        # Query to get the size of the database
        query = "SELECT pg_database_size('feedvault')"
        cursor.execute(sql=query)

        if not cursor:
            return 0

        size_in_bytes = cursor.fetchone()[0]

    if not size_in_bytes:
        return 0

    return int(size_in_bytes / (1024 * 1024))


class IndexView(TemplateView):
    """Index page."""

    template_name = "index.html"

    def get_context_data(self: IndexView, **kwargs: dict) -> dict:
        """Get context data."""
        context = super().get_context_data(**kwargs)
        context["feed_count"] = Feed.objects.count()
        context["database_size"] = get_database_size()
        return context
