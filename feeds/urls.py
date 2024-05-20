from __future__ import annotations

from django.contrib.sitemaps import GenericSitemap
from django.urls import include, path

from feedvault.sitemaps import StaticViewSitemap

from .models import Feed
from .views import AddView, FeedsView, FeedView, IndexView, SearchView, UploadView

app_name: str = "feeds"

sitemaps = {
    "static": StaticViewSitemap,
    "feeds": GenericSitemap({"queryset": Feed.objects.all(), "date_field": "created_at"}),
}

urlpatterns: list = [
    path(route="", view=IndexView.as_view(), name="index"),
    path("__debug__/", include("debug_toolbar.urls")),
    path(route="feed/<int:feed_id>/", view=FeedView.as_view(), name="feed"),
    path(route="feeds/", view=FeedsView.as_view(), name="feeds"),
    path(route="add/", view=AddView.as_view(), name="add"),
    path(route="upload/", view=UploadView.as_view(), name="upload"),
    path(route="search/", view=SearchView.as_view(), name="search"),
]
