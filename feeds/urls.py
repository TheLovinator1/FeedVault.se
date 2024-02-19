from __future__ import annotations

from django.urls import URLPattern, path

from feeds import views

app_name: str = "feeds"

urlpatterns: list[URLPattern] = [
    path(route="", view=views.IndexView.as_view(), name="index"),
    path(route="feed/<int:feed_id>/", view=views.FeedView.as_view(), name="feed"),
    path(route="feeds/", view=views.FeedsView.as_view(), name="feeds"),
    path(route="add", view=views.AddView.as_view(), name="add"),
]
