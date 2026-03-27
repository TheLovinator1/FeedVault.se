from typing import TYPE_CHECKING

from django.urls import path

from . import views

if TYPE_CHECKING:
    from django.urls import URLPattern
    from django.urls import URLResolver


urlpatterns: list[URLPattern | URLResolver] = [
    # /
    path(
        "",
        views.home,
        name="home",
    ),
    # /feeds/
    path(
        "feeds/",
        views.feed_list,
        name="feeds",
    ),
    # /feeds/<feed_id>/
    path(
        "feeds/<int:feed_id>/",
        views.feed_detail,
        name="details",
    ),
    # /feeds/<feed_id>/entries/<entry_id>/
    path(
        "feeds/<int:feed_id>/entries/<int:entry_id>/",
        views.entry_detail,
        name="entry-detail",
    ),
]
