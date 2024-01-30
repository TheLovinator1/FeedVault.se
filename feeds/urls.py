"""URLs for the feeds app."""

from django.urls import path

from feeds.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]
