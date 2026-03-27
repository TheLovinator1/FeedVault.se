from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from feeds.models import Entry
from feeds.models import Feed

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse
    from pytest_django.asserts import QuerySet


def feed_list(request: HttpRequest) -> HttpResponse:
    """View to list all feeds.

    Returns:
        HttpResponse: An HTML response containing the list of feeds.
    """
    feeds = Feed.objects.all().order_by("id")
    return render(request, "feeds/feed_list.html", {"feeds": feeds})


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

    context: dict[str, Feed | QuerySet[Entry, Entry]] = {
        "feed": feed,
        "entries": entries,
    }
    return render(request, "feeds/feed_detail.html", context)


def entry_detail(request: HttpRequest, feed_id: int, entry_id: int) -> HttpResponse:
    """View to display the details of a specific entry.

    Args:
        request (HttpRequest): The HTTP request object.
        feed_id (int): The ID of the feed the entry belongs to.
        entry_id (int): The ID of the entry to display.

    Returns:
        HttpResponse: An HTML response containing the entry details.
    """
    feed: Feed = get_object_or_404(Feed, id=feed_id)
    entry: Entry = get_object_or_404(Entry, id=entry_id, feed=feed)

    # Prepare entry data for display
    if entry.data:
        formatted_json: str = json.dumps(entry.data, indent=2, ensure_ascii=False)
        escaped_json: str | None = html.escape(formatted_json)
    else:
        escaped_json: str | None = None

    context = {
        "feed": feed,
        "entry": entry,
        "escaped_json": escaped_json,
    }
    return render(request, "feeds/entry_detail.html", context)


def home(request: HttpRequest) -> HttpResponse:
    """Redirect to the feed list as the homepage.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the feed list.
    """
    return redirect("/feeds/")
