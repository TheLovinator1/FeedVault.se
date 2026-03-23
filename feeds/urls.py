from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.urls import path

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.urls import URLPattern
    from django.urls import URLResolver


def index(request: HttpRequest) -> HttpResponse:
    """View for the index page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: A simple HTTP response with a greeting message.
    """
    return HttpResponse("Hello, world!")


urlpatterns: list[URLPattern | URLResolver] = [
    path("", index, name="index"),
]
