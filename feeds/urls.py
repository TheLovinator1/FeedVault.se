from __future__ import annotations

from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import URLPattern, path
from django.views.decorators.cache import cache_page

from feeds import views
from feeds.models import Domain, Feed
from feeds.sitemaps import StaticViewSitemap

from .views import APIView, CustomLoginView, CustomLogoutView, ProfileView, RegisterView

app_name: str = "feeds"

sitemaps = {
    "static": StaticViewSitemap,
    "feeds": GenericSitemap({"queryset": Feed.objects.all(), "date_field": "created_at"}),
    "domains": GenericSitemap({"queryset": Domain.objects.all(), "date_field": "created_at"}),
}


# Normal pages
urlpatterns: list[URLPattern] = [
    path(route="", view=views.IndexView.as_view(), name="index"),
    path(route="feed/<int:feed_id>/", view=views.FeedView.as_view(), name="feed"),
    path(route="feeds/", view=views.FeedsView.as_view(), name="feeds"),
    path(route="add", view=views.AddView.as_view(), name="add"),
    path(route="upload", view=views.UploadView.as_view(), name="upload"),
    path(route="robots.txt", view=cache_page(timeout=60 * 60 * 365)(views.RobotsView.as_view()), name="robots"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(route="domains/", view=views.DomainsView.as_view(), name="domains"),
    path(route="domain/<int:domain_id>/", view=views.DomainView.as_view(), name="domain"),
]

# API urls
urlpatterns += [
    path(route="api/", view=APIView.as_view(), name="api"),
    path(route="api/feeds/", view=views.APIFeedsView.as_view(), name="api_feeds"),
    path(route="api/feeds/<int:feed_id>/", view=views.APIFeedView.as_view(), name="api_feeds_id"),
    path(route="api/feeds/<int:feed_id>/entries/", view=views.APIFeedEntriesView.as_view(), name="api_feed_entries"),
    path(route="api/entries/", view=views.APIEntriesView.as_view(), name="api_entries"),
    path(route="api/entries/<int:entry_id>/", view=views.APIEntryView.as_view(), name="api_entries_id"),
]

# Account urls
urlpatterns += [
    path(route="accounts/login/", view=CustomLoginView.as_view(), name="login"),
    path(route="accounts/register/", view=RegisterView.as_view(), name="register"),
    path(route="accounts/logout/", view=CustomLogoutView.as_view(), name="logout"),
    # path(route="accounts/change-password/", view=CustomPasswordChangeView.as_view(), name="change_password"),
    path(route="accounts/profile/", view=ProfileView.as_view(), name="profile"),
]
