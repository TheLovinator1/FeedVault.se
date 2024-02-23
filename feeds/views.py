from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from feeds.add_feeds import add_feed
from feeds.models import Entry, Feed
from feeds.stats import get_db_size

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class IndexView(View):
    """Index path."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context = {
            "db_size": get_db_size(),
            "amount_of_feeds": Feed.objects.count(),
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))


class FeedView(View):
    """A single feed."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003, ARG002
        """Load the feed page."""
        feed_id = kwargs.get("feed_id", None)
        if not feed_id:
            return HttpResponse(content="No id", status=400)

        feed = get_object_or_404(Feed, id=feed_id)
        entries = Entry.objects.filter(feed=feed).order_by("-created_parsed")[:100]

        context = {
            "feed": feed,
            "entries": entries,
            "db_size": get_db_size(),
            "amount_of_feeds": Feed.objects.count(),
            "description": f"Archive of {feed.href}",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": f"{feed.author_detail.name if feed.author_detail else "FeedVault"}",
            "canonical": f"https://feedvault.se/feed/{feed_id}/",
        }

        return render(request, "feed.html", context)


class FeedsView(ListView):
    """All feeds."""

    model = Feed
    paginate_by = 100
    template_name = "feeds.html"
    context_object_name = "feeds"

    def get_context_data(self, **kwargs) -> dict:  # noqa: ANN003
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["db_size"] = get_db_size()
        context["amount_of_feeds"] = Feed.objects.count()
        context["description"] = "Archive of all feeds"
        context["keywords"] = "feed, rss, atom, archive, rss list"
        context["author"] = "TheLovinator"
        context["canonical"] = "https://feedvault.se/feeds/"
        return context


class AddView(View):
    """Add a feed."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context = {
            "db_size": get_db_size(),
            "amount_of_feeds": Feed.objects.count(),
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))

    def post(self, request: HttpRequest) -> HttpResponse:
        """Add a feed."""
        urls: str | None = request.POST.get("urls", None)
        if not urls:
            return HttpResponse(content="No urls", status=400)

        # Split the urls by newline.
        for url in urls.split("\n"):
            feed: None | Feed = add_feed(url)
            if not feed:
                messages.error(request, f"{url} - Failed to add")
                continue
            # Check if bozo is true.
            if feed.bozo:
                messages.warning(request, f"{feed.feed_url} - Bozo: {feed.bozo_exception}")

            messages.success(request, f"{feed.feed_url} added")

        # Render the index page.
        template = loader.get_template(template_name="index.html")
        return HttpResponse(content=template.render(context={}, request=request))


class UploadView(View):
    """Upload a file."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context = {
            "db_size": get_db_size(),
            "amount_of_feeds": Feed.objects.count(),
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))

    def post(self, request: HttpRequest) -> HttpResponse:
        """Upload a file."""
        file = request.FILES.get("file", None)
        if not file:
            return HttpResponse(content="No file", status=400)

        # Split the urls by newline.
        for url in file.read().decode("utf-8").split("\n"):
            feed: None | Feed = add_feed(url)
            if not feed:
                messages.error(request, f"{url} - Failed to add")
                continue
            # Check if bozo is true.
            if feed.bozo:
                messages.warning(request, f"{feed.feed_url} - Bozo: {feed.bozo_exception}")

            messages.success(request, f"{feed.feed_url} added")

        # Render the index page.
        template = loader.get_template(template_name="index.html")
        return HttpResponse(content=template.render(context={}, request=request))


class CustomLoginView(LoginView):
    """Custom login view."""

    template_name = "accounts/login.html"

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        """Check if the form is valid."""
        user: User = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class RegisterView(CreateView):
    """Register view."""

    template_name = "accounts/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("feeds:login")


class CustomLogoutView(LogoutView):
    """Logout view."""

    next_page = "feeds:index"  # Redirect to index after logout


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """Custom password change view."""

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("feeds:index")
    success_message = "Your password was successfully updated!"


class ProfileView(View):
    """Profile page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the profile page."""
        template = loader.get_template(template_name="accounts/profile.html")
        context = {
            "db_size": get_db_size(),
            "amount_of_feeds": Feed.objects.count(),
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))


class APIView(View):
    """API documentation page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the API page."""
        template = loader.get_template(template_name="api.html")
        context = {
            "db_size": get_db_size(),
            "amount_of_feeds": Feed.objects.count(),
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/api/",
        }
        return HttpResponse(content=template.render(context=context, request=request))
