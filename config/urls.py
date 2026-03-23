from typing import TYPE_CHECKING

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.urls import path

if TYPE_CHECKING:
    from django.urls import URLPattern
    from django.urls.resolvers import URLResolver

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include("feeds.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.TESTING:
    from debug_toolbar.toolbar import (  # pyright: ignore[reportMissingTypeStubs]
        debug_toolbar_urls,
    )

    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
    urlpatterns = [*urlpatterns, *debug_toolbar_urls()]
