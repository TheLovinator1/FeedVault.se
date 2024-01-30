"""URL configuration for feedvault project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import URLResolver, include, path

urlpatterns: list[URLResolver] = [
    path(route="admin/", view=admin.site.urls),
    path(route="__debug__/", view=include(arg="debug_toolbar.urls")),
    path(route="", view=include(arg="feeds.urls")),
]
