from __future__ import annotations

from django.urls import URLPattern, path

from feeds import views

from .views import APIView, CustomLoginView, CustomLogoutView, ProfileView, RegisterView

app_name: str = "feeds"

urlpatterns: list[URLPattern] = [
    path(route="", view=views.IndexView.as_view(), name="index"),
    path(route="feed/<int:feed_id>/", view=views.FeedView.as_view(), name="feed"),
    path(route="feeds/", view=views.FeedsView.as_view(), name="feeds"),
    path(route="add", view=views.AddView.as_view(), name="add"),
    path(route="upload", view=views.UploadView.as_view(), name="upload"),
    path(route="api/", view=APIView.as_view(), name="api"),
]

# Account urls
urlpatterns += [
    path(route="accounts/login/", view=CustomLoginView.as_view(), name="login"),
    path(route="accounts/register/", view=RegisterView.as_view(), name="register"),
    path(route="accounts/logout/", view=CustomLogoutView.as_view(), name="logout"),
    # path(route="accounts/change-password/", view=CustomPasswordChangeView.as_view(), name="change_password"),
    path(route="accounts/profile/", view=ProfileView.as_view(), name="profile"),
]
