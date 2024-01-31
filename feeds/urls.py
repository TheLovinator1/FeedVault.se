"""URLs for the feeds app."""

from django.urls import path

from feeds.views import APIView, DonateView, FeedsView, IndexView, add_feeds

app_name = "feeds"

urlpatterns = [
    # /
    path("", IndexView.as_view(), name="index"),
    # /feeds
    path("feeds", FeedsView.as_view(), name="feeds"),
    # /add
    path("add", add_feeds, name="add"),
    # /api
    path("api", APIView.as_view(), name="api"),
    # /donate
    path("donate", DonateView.as_view(), name="donate"),
]
