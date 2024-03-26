from __future__ import annotations

from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.cache import cache_page

from feedvault import views
from feedvault.api import api_v1
from feedvault.models import Domain, Feed
from feedvault.sitemaps import StaticViewSitemap
from feedvault.views import CustomLoginView, CustomLogoutView, ProfileView, RegisterView

app_name: str = "feedvault"

sitemaps = {
    "static": StaticViewSitemap,
    "feeds": GenericSitemap({"queryset": Feed.objects.all(), "date_field": "created_at"}),
    "domains": GenericSitemap({"queryset": Domain.objects.all(), "date_field": "created_at"}),
}

urlpatterns: list = [
    path(route="", view=views.IndexView.as_view(), name="index"),
    path("__debug__/", include("debug_toolbar.urls")),
    path(route="feed/<int:feed_id>/", view=views.FeedView.as_view(), name="feed"),
    path(route="feeds/", view=views.FeedsView.as_view(), name="feeds"),
    path(route="add/", view=views.AddView.as_view(), name="add"),
    path(route="upload/", view=views.UploadView.as_view(), name="upload"),
    path(route="download/", view=views.DownloadView.as_view(), name="download"),
    path(route="delete_upload/", view=views.DeleteUploadView.as_view(), name="delete_upload"),
    path(route="edit_description/", view=views.EditDescriptionView.as_view(), name="edit_description"),
    path(route="robots.txt", view=cache_page(timeout=60 * 60 * 365)(views.RobotsView.as_view()), name="robots"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(route="search/", view=views.SearchView.as_view(), name="search"),
    path(route="domains/", view=views.DomainsView.as_view(), name="domains"),
    path(route="domain/<int:domain_id>/", view=views.DomainView.as_view(), name="domain"),
    path("api/v1/", api_v1.urls),  # type: ignore  # noqa: PGH003
    path(route="accounts/login/", view=CustomLoginView.as_view(), name="login"),
    path(route="accounts/register/", view=RegisterView.as_view(), name="register"),
    path(route="accounts/logout/", view=CustomLogoutView.as_view(), name="logout"),
    # path(route="accounts/change-password/", view=CustomPasswordChangeView.as_view(), name="change_password"),
    path(route="accounts/profile/", view=ProfileView.as_view(), name="profile"),
]
