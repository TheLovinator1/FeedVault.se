from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views import View


class IndexView(View):
    """Index path."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """GET request for index path."""
        template = loader.get_template(template_name="index.html")
        context = {}
        return HttpResponse(content=template.render(context=context, request=request))


class FeedView(View):
    """A single feed."""

    def get(self, request: HttpRequest, feed_id: int) -> HttpResponse:
        """GET request for index path."""
        template = loader.get_template(template_name="feed.html")
        context = {"feed_id": feed_id}
        return HttpResponse(content=template.render(context=context, request=request))


class FeedsView(View):
    """All feeds."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """GET request for index path."""
        template = loader.get_template(template_name="feeds.html")
        context = {}
        return HttpResponse(content=template.render(context=context, request=request))
