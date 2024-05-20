from __future__ import annotations

from django.contrib.sitemaps import GenericSitemap, Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.cache import cache_page

from feeds.models import Feed
from feedvault import views
from feedvault.sitemaps import StaticViewSitemap

app_name: str = "feedvault"

sitemaps: dict[str, type[Sitemap] | Sitemap] = {
    "static": StaticViewSitemap,
    "feeds": GenericSitemap({"queryset": Feed.objects.all(), "date_field": "created_at"}),
}

urlpatterns: list = [
    path(route="", view=include("feeds.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path(route="robots.txt", view=cache_page(timeout=60 * 60 * 365)(views.RobotsView.as_view()), name="robots"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
