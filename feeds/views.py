from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.core.paginator import EmptyPage, Page, Paginator
from django.db.models.manager import BaseManager
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.views import View
from reader import InvalidFeedURLError

from feeds.get_reader import get_reader
from feeds.models import Entry, Feed, UploadedFeed

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models.manager import BaseManager
    from reader import Reader

logger: logging.Logger = logging.getLogger(__name__)


class HtmxHttpRequest(HttpRequest):
    htmx: Any


class IndexView(View):
    """Index path."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context: dict[str, str] = {
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
            "title": "FeedVault",
        }
        return HttpResponse(content=template.render(context=context, request=request))


class FeedView(View):
    """A single feed."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003
        """Load the feed page."""
        feed_id: str = kwargs.get("feed_id", None)
        if not feed_id:
            return HttpResponse(content="No id", status=400)

        feed: Feed = get_object_or_404(Feed, pk=feed_id)
        entries: BaseManager[Entry] = Entry.objects.filter(feed=feed).order_by("-added")[:100]

        context: dict[str, Any] = {
            "feed": feed,
            "entries": entries,
            "description": f"{feed.subtitle}" or f"Archive of {feed.url}",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": f"{feed.author}" or "FeedVault",
            "canonical": f"https://feedvault.se/feed/{feed.pk}/",
            "title": f"{feed.title}" or "FeedVault",
        }

        return render(request=request, template_name="feed.html", context=context)


class FeedsView(View):
    """All feeds."""

    def get(self, request: HtmxHttpRequest) -> HttpResponse:
        """All feeds."""
        feeds: BaseManager[Feed] = Feed.objects.only("id", "url")

        paginator = Paginator(object_list=feeds, per_page=100)
        page_number = int(request.GET.get("page", default=1))

        try:
            pages: Page = paginator.get_page(page_number)
        except EmptyPage:
            return HttpResponse("")

        context: dict[str, str | Page | int] = {
            "feeds": pages,
            "description": "An archive of web feeds",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/feeds/",
            "title": "Feeds",
            "page": page_number,
        }

        template_name = "partials/feeds.html" if request.htmx else "feeds.html"
        return render(request, template_name, context)


class AddView(View):
    """Add a feed."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context: dict[str, str] = {
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))

    def post(self, request: HttpRequest) -> HttpResponse:
        """Add a feed."""
        urls: str | None = request.POST.get("urls", None)
        if not urls:
            return HttpResponse(content="No urls", status=400)

        reader: Reader = get_reader()
        for url in urls.split("\n"):
            clean_url: str = url.strip()
            try:
                reader.add_feed(clean_url)
                messages.success(request, f"Added {clean_url}")
            except InvalidFeedURLError:
                logger.exception("Error adding %s", clean_url)
                messages.error(request, f"Error adding {clean_url}")

        messages.success(request, "Feeds added")
        return redirect("feeds:index")


class UploadView(View):
    """Upload a file."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Upload a file."""
        file: UploadedFile | None = request.FILES.get("file", None)
        if not file:
            return HttpResponse(content="No file", status=400)

        # Save file to media folder
        UploadedFeed.objects.create(user=request.user, file=file, original_filename=file.name)

        # Render the index page.
        messages.success(request, f"{file.name} uploaded")
        messages.info(request, "If the file was marked as public, it will be shown on the feeds page. ")
        return redirect("feeds:index")


class SearchView(View):
    """Search view."""

    def get(self, request: HtmxHttpRequest) -> HttpResponse:
        """Load the search page."""
        query: str | None = request.GET.get("q", None)
        if not query:
            return FeedsView().get(request)

        # TODO(TheLovinator): #20 Search more fields
        # https://github.com/TheLovinator1/FeedVault/issues/20
        feeds: BaseManager[Feed] = Feed.objects.filter(url__icontains=query).order_by("-added")[:100]

        context = {
            "feeds": feeds,
            "description": f"Search results for {query}",
            "keywords": f"feed, rss, atom, archive, rss list, {query}",
            "author": "TheLovinator",
            "canonical": f"https://feedvault.se/search/?q={query}",
            "title": f"Search results for {query}",
            "query": query,
        }

        return render(request, "search.html", context)
