from typing import TYPE_CHECKING

from django.urls import path

from . import views

if TYPE_CHECKING:
    from django.urls import URLPattern
    from django.urls import URLResolver


urlpatterns: list[URLPattern | URLResolver] = [
    path("", views.feed_list, name="feed-list"),
    path("feeds/<int:feed_id>/", views.feed_detail, name="feed-detail"),
    path(
        "feeds/<int:feed_id>/entries/<int:entry_id>/",
        views.entry_detail,
        name="entry-detail",
    ),
]
