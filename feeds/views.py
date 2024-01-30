"""Views for the feeds app.

IndexView - /
FeedsView - /feeds
"""

from __future__ import annotations

import logging
import typing
from urllib import parse

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import connection
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from feeds.models import Blocklist, Feed
from feeds.validator import is_ip, is_local, validate_scheme

if typing.TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger: logging.Logger = logging.getLogger(__name__)


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

        logger.info(f"Found {context['feed_count']} feeds in the database")  # noqa: G004
        logger.info(f"Database size is {context['database_size']} MB")  # noqa: G004
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


def add_feeds(request: HttpRequest) -> HttpResponse:
    """Add feeds to the database.

    Args:
        request: The request object.

    Returns:
        A redirect to the index page if there are errors, otherwise a redirect to the feeds page.
    """
    if request.method == "POST":
        urls: str | None = request.POST.get("urls")
        if not urls:
            messages.error(request, "No URLs provided")
            return redirect("feeds:index")

        if urls == "Test":
            messages.error(request, "Test test hello")
            return redirect("feeds:index")

        for url in urls.splitlines():
            check_feeds(feed_urls=[url], request=request)

        return redirect("feeds:index")

    msg: str = f"You must use a POST request. You used a {request.method} request. You can find out how to use this endpoint here: <a href=''>http://127.0.0.1:8000/</a>. If you think this is a mistake, please contact the administrator."  # noqa: E501
    messages.error(request, msg)
    return redirect("feeds:index")


def check_feeds(feed_urls: list[str], request: HttpRequest) -> HttpResponse:
    """Check feeds before adding them to the database.

    Args:
        feed_urls: The feed URLs to check.
        request: The request object.

    Returns:
        A redirect to the index page if there are errors, otherwise a redirect to the feeds page.
    """
    for url in feed_urls:
        url_html: str = f"<a href='{url}'>{url}</a>"
        if Feed.objects.filter(url=url).exists():
            msg: str = f"{url_html} is already in the database."
            messages.error(request, msg)
            continue

        # Only allow HTTP and HTTPS URLs
        if not validate_scheme(feed_url=url):
            msg = f"{url_html} is not a HTTP or HTTPS URL."
            messages.error(request, msg)
            continue

        # Don't allow IP addresses
        if is_ip(feed_url=url):
            msg = f"{url_html} is an IP address. IP addresses are not allowed."
            messages.error(request, msg)
            continue

        # Check if in blocklist
        domain: str = parse.urlparse(url).netloc
        if Blocklist.objects.filter(url=domain).exists():
            msg = f"{url_html} is in the blocklist."
            messages.error(request, msg)
            continue

        # Check if local URL
        if is_local(feed_url=url):
            msg = f"{url_html} is a local URL."
            messages.error(request, msg)
            continue

        # Create feed
        try:
            Feed.objects.create(url=url)
            msg = f"{url_html} was added to the database."
            messages.success(request, msg)
        except ValidationError:
            msg = f"{url_html} is not a valid URL."
            messages.error(request, msg)

    # Return to feeds page if no errors
    # TODO(TheLovinator): Return to search page with our new feeds  # noqa: TD003
    logger.info(f"Added {len(feed_urls)} feeds to the database")  # noqa: G004
    return redirect("feeds:feeds")


class APIView(TemplateView):
    """Index page."""

    template_name = "api.html"

    def get_context_data(self: APIView, **kwargs: dict) -> dict:
        """Add feed count and database size to context data."""
        context: dict = super().get_context_data(**kwargs)
        context["feed_count"] = Feed.objects.count()
        context["database_size"] = get_database_size()
        return context


def upload_opml(request: HttpRequest) -> HttpResponse:
    """Add feeds to the database.

    Args:
        request: The request object.

    Returns:
        A redirect to the index page if there are errors, otherwise a redirect to the feeds page.
    """
    if request.method == "POST":
        opml: str | None = request.POST.get("opml")
        if not opml:
            messages.error(request, "No OPML provided")
            return redirect("feeds:feeds")

    return redirect("feeds:feeds")
