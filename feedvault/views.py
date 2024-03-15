from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.manager import BaseManager
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from feedvault.add_feeds import add_feed
from feedvault.models import Domain, Entry, Feed

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models.manager import BaseManager


class IndexView(View):
    """Index path."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context = {
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
            "title": "FeedVault",
        }
        return HttpResponse(content=template.render(context=context, request=request))


class FeedView(View):
    """A single feed."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003, ARG002
        """Load the feed page."""
        feed_id = kwargs.get("feed_id", None)
        if not feed_id:
            return HttpResponse(content="No id", status=400)

        feed: Feed = get_object_or_404(Feed, id=feed_id)
        entries: BaseManager[Entry] = Entry.objects.filter(feed=feed).order_by("-created_parsed")[:100]

        context = {
            "feed": feed,
            "entries": entries,
            "description": f"Archive of {feed.href}",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": f"{feed.author_detail.name if feed.author_detail else "FeedVault"}",
            "canonical": f"https://feedvault.se/feed/{feed_id}/",
            "title": f"{feed.title} - FeedVault",
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
        feed_amount: int = Feed.objects.count() or 0
        context["description"] = f"Archiving {feed_amount} feeds"
        context["keywords"] = "feed, rss, atom, archive, rss list"
        context["author"] = "TheLovinator"
        context["canonical"] = "https://feedvault.se/feeds/"
        context["title"] = "Feeds"
        return context


class AddView(View):
    """Add a feed."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the index page."""
        template = loader.get_template(template_name="index.html")
        context: dict[str, str] = {
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))

    def post(self, request: HttpRequest) -> HttpResponse:
        """Add a feed."""
        if not request.user.is_authenticated:
            return HttpResponse(content="Not logged in", status=401)

        if not request.user.is_active:
            return HttpResponse(content="User is not active", status=403)

        urls: str | None = request.POST.get("urls", None)
        if not urls:
            return HttpResponse(content="No urls", status=400)

        # Split the urls by newline.
        for url in urls.split("\n"):
            feed: None | Feed = add_feed(url, request.user)
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
        context: dict[str, str] = {
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/",
        }
        return HttpResponse(content=template.render(context=context, request=request))

    def post(self, request: HttpRequest) -> HttpResponse:
        """Upload a file."""
        if not request.user.is_authenticated:
            return HttpResponse(content="Not logged in", status=401)

        if not request.user.is_active:
            return HttpResponse(content="User is not active", status=403)

        file: UploadedFile | None = request.FILES.get("file", None)
        if not file:
            return HttpResponse(content="No file", status=400)

        # Split the urls by newline.
        for url in file.read().decode("utf-8").split("\n"):
            feed: None | Feed = add_feed(url, request.user)
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
    success_url = reverse_lazy("login")

    # Add context data to the view
    def get_context_data(self, **kwargs) -> dict:  # noqa: ANN003
        """Get the context data."""
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["description"] = "Register a new account"
        context["keywords"] = "register, account, feed, rss, atom, archive, rss list"
        context["author"] = "TheLovinator"
        context["canonical"] = "https://feedvault.se/accounts/register/"
        context["title"] = "Register"
        return context


class CustomLogoutView(LogoutView):
    """Logout view."""

    next_page = "index"  # Redirect to index after logout


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """Custom password change view."""

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("index")
    success_message = "Your password was successfully updated!"

    # Add context data to the view
    def get_context_data(self, **kwargs) -> dict:  # noqa: ANN003
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["description"] = "Change your password"
        context["keywords"] = "change, password, account, feed, rss, atom, archive, rss list"
        context["author"] = "TheLovinator"
        context["canonical"] = "https://feedvault.se/accounts/change-password/"
        context["title"] = "Change password"
        return context


class ProfileView(View):
    """Profile page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the profile page."""
        template = loader.get_template(template_name="accounts/profile.html")

        user_feeds: BaseManager[Feed] = Feed.objects.filter(user=request.user).order_by("-created_at")[:100]

        context: dict[str, str | Any] = {
            "description": f"Profile page for {request.user.get_username()}",
            "keywords": f"profile, account, {request.user.get_username()}",
            "author": f"{request.user.get_username()}",
            "canonical": "https://feedvault.se/accounts/profile/",
            "title": f"{request.user.get_username()}",
            "user_feeds": user_feeds,
        }
        return HttpResponse(content=template.render(context=context, request=request))


class RobotsView(View):
    """Robots.txt view."""

    def get(self, request: HttpRequest) -> HttpResponse:  # noqa: ARG002
        """Load the robots.txt file."""
        return HttpResponse(
            content="User-agent: *\nDisallow: /add\nDisallow: /upload\nDisallow: /accounts/",
            content_type="text/plain",
        )


class DomainsView(View):
    """All domains."""

    def get(self: DomainsView, request: HttpRequest) -> HttpResponse:
        """Load the domains page."""
        domains: BaseManager[Domain] = Domain.objects.all()
        template = loader.get_template(template_name="domains.html")
        context = {
            "domains": domains,
            "description": "Domains",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/domains/",
            "title": "Domains",
        }
        return HttpResponse(content=template.render(context=context, request=request))


class DomainView(View):
    """A single domain."""

    def get(self: DomainView, request: HttpRequest, domain_id: int) -> HttpResponse:
        """Load the domain page."""
        domain: Domain = get_object_or_404(Domain, id=domain_id)
        feeds: BaseManager[Feed] = Feed.objects.filter(domain=domain).order_by("-created_at")[:100]

        context = {
            "domain": domain,
            "feeds": feeds,
            "description": f"Archive of {domain.name}",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": f"https://feedvault.se/domain/{domain_id}/",
            "title": f"{domain.name} - FeedVault",
        }

        return render(request, "domain.html", context)
