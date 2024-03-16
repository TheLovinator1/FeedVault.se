from __future__ import annotations

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static views."""

    changefreq: str = "daily"
    priority: float = 0.5

    def items(self: StaticViewSitemap) -> list[str]:
        """Return all the items in the sitemap."""
        return ["index", "feeds", "domains"]

    def location(self: StaticViewSitemap, item: str) -> str:
        """Return the location of the item."""
        return reverse(item)
