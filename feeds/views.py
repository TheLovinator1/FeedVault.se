from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from feeds.models import Entry
from feeds.models import Feed

if TYPE_CHECKING:
    from django.http import HttpRequest
    from pytest_django.asserts import QuerySet


def feed_list(request: HttpRequest) -> HttpResponse:
    """View to list all feeds.

    Returns:
        HttpResponse: An HTML response containing the list of feeds.
    """
    feeds = Feed.objects.all().order_by("id")
    html = [
        "<!DOCTYPE html>",
        "<html><head><title>FeedVault - Feeds</title></head><body>",
        "<h1>Feed List</h1>",
        "<ul>",
    ]
    html.extend(
        f'<li><a href="/feeds/{feed.pk}/">{feed.url}</a></li>' for feed in feeds
    )
    html.extend(("</ul>", "</body></html>"))
    return HttpResponse("\n".join(html))


def feed_detail(request: HttpRequest, feed_id: int) -> HttpResponse:
    """View to display the details of a specific feed.

    Args:
        request (HttpRequest): The HTTP request object.
        feed_id (int): The ID of the feed to display.

    Returns:
        HttpResponse: An HTML response containing the feed details and its entries.
    """
    feed: Feed = get_object_or_404(Feed, id=feed_id)

    entries: QuerySet[Entry, Entry] = Entry.objects.filter(feed=feed).order_by(
        "-published_at",
        "-fetched_at",
    )[:50]
    html: list[str] = [
        "<!DOCTYPE html>",
        f"<html><head><title>FeedVault - {feed.url}</title></head><body>",
        "<h1>Feed Detail</h1>",
        f"<p><b>URL:</b> {feed.url}</p>",
        f"<p><b>Domain:</b> {feed.domain}</p>",
        f"<p><b>Active:</b> {'yes' if feed.is_active else 'no'}</p>",
        f"<p><b>Created:</b> {feed.created_at}</p>",
        f"<p><b>Last fetched:</b> {feed.last_fetched_at}</p>",
        "<h2>Entries (latest 50)</h2>",
        "<ul>",
    ]
    for entry in entries:
        title: str | None = entry.data.get("title") if entry.data else None
        summary: str | None = entry.data.get("summary") if entry.data else None
        snippet: str = title or summary or "[no title]"
        html.append(
            f"<li><b>{entry.published_at or entry.fetched_at}:</b> {snippet} <small>(id: {entry.entry_id})</small></li>",
        )
    html.extend(("</ul>", '<p><a href="/">Back to list</a></p>', "</body></html>"))
    return HttpResponse("\n".join(html))
