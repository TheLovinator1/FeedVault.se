"""Views for the feeds app.

IndexView - /
FeedsView - /feeds
"""

from __future__ import annotations

import typing

from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from feeds.models import Feed

if typing.TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponseRedirect


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

        size_in_bytes = cursor.fetchone()[0]  # type: ignore  # noqa: PGH003

    if not size_in_bytes:
        return 0

    return int(size_in_bytes / (1024 * 1024))


class IndexView(TemplateView):
    """Index page."""

    template_name = "index.html"

    def get_context_data(self: IndexView, **kwargs: dict) -> dict:
        """Add feed count and database size to context data."""
        context: dict = super().get_context_data(**kwargs)
        context["feed_count"] = Feed.objects.count()
        context["database_size"] = get_database_size()
        return context


class FeedsView(ListView):
    """Feeds page."""

    model = Feed
    template_name = "feeds.html"
    context_object_name = "feeds"
    paginate_by = 100
    ordering: typing.ClassVar[list[str]] = ["-created_at"]

    def get_context_data(self: FeedsView, **kwargs: dict) -> dict:
        """Add feed count and database size to context data."""
        context: dict = super().get_context_data(**kwargs)
        context["feed_count"] = Feed.objects.count()
        context["database_size"] = get_database_size()
        return context


def add_feeds(request: HttpRequest) -> HttpResponseRedirect:
    """Add feeds to the database.

    Args:
        request: The request object.

    Returns:
        A redirect to the index page.
    """
    if request.method == "POST":
        urls = request.POST.get("urls")
        if not urls:
            messages.error(request, "No URLs provided")
            return redirect("feeds:index", permanent=False)

        if urls == "Test":
            messages.error(request, "Hello, world!")
            return redirect("feeds:index", permanent=False)

        for url in urls.splitlines():
            print(f"Adding {url} to the database...")  # noqa: T201

        return redirect("feeds:feeds", permanent=False)

    msg: str = f"You must use a POST request. You used a {request.method} request. You can find out how to use this endpoint here: <a href=''>http://127.0.0.1:8000/</a>. If you think this is a mistake, please contact the administrator."  # noqa: E501
    messages.error(request, msg)
    return redirect("feeds:index", permanent=False)


class APIView(TemplateView):
    """Index page."""

    template_name = "api.html"

    def get_context_data(self: APIView, **kwargs: dict) -> dict:
        """Add feed count and database size to context data."""
        context: dict = super().get_context_data(**kwargs)
        context["feed_count"] = Feed.objects.count()
        context["database_size"] = get_database_size()
        return context
