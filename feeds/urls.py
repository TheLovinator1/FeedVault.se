"""URLs for the feeds app."""

from django.urls import path

from feeds.views import FeedsView, IndexView

app_name = "feeds"

urlpatterns = [
    # /
    path("", IndexView.as_view(), name="index"),
    # /feeds
    path("feeds", FeedsView.as_view(), name="feeds"),
]
