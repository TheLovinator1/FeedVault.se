from __future__ import annotations

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static views."""

    changefreq: str = "daily"
    priority: float = 0.5

    def items(self: StaticViewSitemap) -> list[str]:
        """Return all the items in the sitemap."""
        return ["feeds:index", "feeds:feeds", "feeds:domains"]

    def location(self, item) -> str:
        return reverse(item)
