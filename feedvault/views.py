from django.http import HttpRequest, HttpResponse
from django.views import View


class RobotsView(View):
    """Robots.txt view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the robots.txt file."""
        return HttpResponse(
            content="User-agent: *\nDisallow: /add\nDisallow: /upload\nDisallow: /accounts/\n\nSitemap: https://feedvault.se/sitemap.xml",
            content_type="text/plain",
        )
