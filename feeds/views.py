from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from feeds.add_feeds import add_feed
from feeds.models import Entry, Feed

if TYPE_CHECKING:
    from django.contrib.auth.models import User


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

        feed = get_object_or_404(Feed, id=feed_id)
        entries = Entry.objects.filter(feed=feed).order_by("-created_parsed")[:100]

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
        context = {
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
        context = {
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

        file = request.FILES.get("file", None)
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
    success_url = reverse_lazy("feeds:login")

    # Add context data to the view
    def get_context_data(self, **kwargs) -> dict:  # noqa: ANN003
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["description"] = "Register a new account"
        context["keywords"] = "register, account, feed, rss, atom, archive, rss list"
        context["author"] = "TheLovinator"
        context["canonical"] = "https://feedvault.se/accounts/register/"
        context["title"] = "Register"
        return context


class CustomLogoutView(LogoutView):
    """Logout view."""

    next_page = "feeds:index"  # Redirect to index after logout


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """Custom password change view."""

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("feeds:index")
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

        user_feeds = Feed.objects.filter(user=request.user).order_by("-created_at")[:100]

        context: dict[str, str | Any] = {
            "description": f"Profile page for {request.user.get_username()}",
            "keywords": f"profile, account, {request.user.get_username()}",
            "author": f"{request.user.get_username()}",
            "canonical": "https://feedvault.se/accounts/profile/",
            "title": f"{request.user.get_username()}",
            "user_feeds": user_feeds,
        }
        return HttpResponse(content=template.render(context=context, request=request))


class APIView(View):
    """API documentation page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the API page."""
        template = loader.get_template(template_name="api.html")
        context = {
            "description": "FeedVault allows users to archive and search their favorite web feeds.",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/api/",
            "title": "API Documentation",
        }
        return HttpResponse(content=template.render(context=context, request=request))


class RobotsView(View):
    """Robots.txt view."""

    def get(self, request: HttpRequest) -> HttpResponse:  # noqa: ARG002
        """Load the robots.txt file."""
        return HttpResponse(
            content="""User-agent: *\nDisallow: /add\nDisallow: /upload\nDisallow: /accounts/""",
            content_type="text/plain",
        )


class APIFeedsView(View):
    """API Feeds view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get all feeds with pagination."""
        # Retrieve all feeds
        feeds_list = Feed.objects.all()

        # Pagination settings
        page: int = int(request.GET.get("page", 1))  # Get the page number from the query parameters, default to 1
        per_page: int = int(request.GET.get("per_page", 1000))  # Number of feeds per page, default to 1000 (max 1000)

        # Add a ceiling to the per_page value
        max_per_page = 1000
        if per_page > max_per_page:
            per_page = max_per_page

        # Create Paginator instance
        paginator = Paginator(feeds_list, per_page)

        try:
            feeds: Page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            feeds = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            feeds = paginator.page(paginator.num_pages)

        # Convert feeds to dictionary
        feeds_dict = [model_to_dict(feed) for feed in feeds]

        # Return the paginated entries as JsonResponse
        response = JsonResponse(feeds_dict, safe=False)

        # Add pagination headers
        response["X-Page"] = feeds.number
        response["X-Page-Count"] = paginator.num_pages
        response["X-Per-Page"] = per_page
        response["X-Total-Count"] = paginator.count
        response["X-First-Page"] = 1
        response["X-Last-Page"] = paginator.num_pages

        # Next and previous page links
        if feeds.has_next():
            response["X-Next-Page"] = feeds.next_page_number()
        if feeds.has_previous():
            response["X-Prev-Page"] = feeds.previous_page_number()

        return response


class APIFeedView(View):
    """API Feed view."""

    def get(self, request: HttpRequest, feed_id: int) -> HttpResponse:  # noqa: ARG002
        """Get a single feed."""
        feed = get_object_or_404(Feed, id=feed_id)
        return JsonResponse(model_to_dict(feed), safe=False)


class APIEntriesView(View):
    """API Entries view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get all entries with pagination."""
        # Retrieve all entries
        entries_list = Entry.objects.all()

        # Pagination settings
        page: int = int(request.GET.get("page", 1))  # Get the page number from the query parameters, default to 1
        per_page: int = int(request.GET.get("per_page", 1000))

        # Add a ceiling to the per_page value
        max_per_page = 1000
        if per_page > max_per_page:
            per_page = max_per_page

        # Create Paginator instance
        paginator = Paginator(entries_list, per_page)

        try:
            entries: Page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            entries = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            entries = paginator.page(paginator.num_pages)

        # Convert entries to dictionary
        entries_dict = [model_to_dict(entry) for entry in entries]

        # Return the paginated entries as JsonResponse
        response = JsonResponse(entries_dict, safe=False)

        # Add pagination headers
        response["X-Page"] = entries.number
        response["X-Page-Count"] = paginator.num_pages
        response["X-Per-Page"] = per_page
        response["X-Total-Count"] = paginator.count
        response["X-First-Page"] = 1
        response["X-Last-Page"] = paginator.num_pages

        # Next and previous page links
        if entries.has_next():
            response["X-Next-Page"] = entries.next_page_number()
        if entries.has_previous():
            response["X-Prev-Page"] = entries.previous_page_number()

        return response


class APIEntryView(View):
    """API Entry view."""

    def get(self, request: HttpRequest, entry_id: int) -> HttpResponse:  # noqa: ARG002
        """Get a single entry."""
        entry = get_object_or_404(Entry, id=entry_id)
        return JsonResponse(model_to_dict(entry), safe=False)


class APIFeedEntriesView(View):
    """API Feed Entries view."""

    def get(self, request: HttpRequest, feed_id: int) -> HttpResponse:
        """Get all entries for a single feed with pagination."""
        # Retrieve all entries for a single feed
        entries_list = Entry.objects.filter(feed_id=feed_id)

        # Pagination settings
        page: int = int(request.GET.get("page", 1))  # Get the page number from the query parameters, default to 1
        per_page: int = int(request.GET.get("per_page", 1000))

        # Add a ceiling to the per_page value
        max_per_page = 1000
        if per_page > max_per_page:
            per_page = max_per_page

        # Create Paginator instance
        paginator = Paginator(entries_list, per_page)

        try:
            entries: Page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            entries = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            entries = paginator.page(paginator.num_pages)

        # Convert entries to dictionary
        entries_dict = [model_to_dict(entry) for entry in entries]

        # Return the paginated entries as JsonResponse
        response = JsonResponse(entries_dict, safe=False)

        # Add pagination headers
        response["X-Page"] = entries.number
        response["X-Page-Count"] = paginator.num_pages
        response["X-Per-Page"] = per_page
        response["X-Total-Count"] = paginator.count
        response["X-First-Page"] = 1
        response["X-Last-Page"] = paginator.num_pages

        # Next and previous page links
        if entries.has_next():
            response["X-Next-Page"] = entries.next_page_number()
        if entries.has_previous():
            response["X-Prev-Page"] = entries.previous_page_number()

        return response

