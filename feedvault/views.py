from __future__ import annotations

import logging
from mimetypes import guess_type
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import SuspiciousOperation
from django.core.paginator import EmptyPage, Page, Paginator
from django.db.models.manager import BaseManager
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView

from feedvault.feeds import add_url
from feedvault.models import Domain, Entry, Feed, FeedAddResult, UserUploadedFile

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models.manager import BaseManager

logger: logging.Logger = logging.getLogger(__name__)


class HtmxHttpRequest(HttpRequest):
    htmx: Any


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


class FeedsView(View):
    """All feeds."""

    def get(self, request: HtmxHttpRequest) -> HttpResponse:
        """All feeds."""
        feeds: BaseManager[Feed] = Feed.objects.only("id", "feed_url")

        paginator = Paginator(object_list=feeds, per_page=100)
        page_number = int(request.GET.get("page", default=1))

        try:
            pages: Page = paginator.get_page(page_number)
        except EmptyPage:
            return HttpResponse("")

        context: dict[str, str | Page | int] = {
            "feeds": pages,
            "description": "An archive of all feeds",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/feeds/",
            "title": "Feeds",
            "page": page_number,
        }

        template_name = "partials/feeds.html" if request.htmx else "feeds.html"
        return render(request, template_name, context)


class AddView(LoginRequiredMixin, View):
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
            feed_result: FeedAddResult = add_url(url, request.user)
            feed: Feed | None = feed_result.feed
            if not feed_result or not feed:
                messages.error(request, f"{url} - Failed to add, {feed_result.error}")
                continue
            if feed_result.created:
                messages.success(request, f"{feed.feed_url} added to queue")
            else:
                messages.warning(request, f"{feed.feed_url} already exists")

        # Render the index page.
        template = loader.get_template(template_name="index.html")
        return HttpResponse(content=template.render(context={}, request=request))


class UploadView(LoginRequiredMixin, View):
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

        # Save file to media folder
        UserUploadedFile.objects.create(user=request.user, file=file, original_filename=file.name)

        # Render the index page.
        template = loader.get_template(template_name="index.html")
        messages.success(request, f"{file.name} uploaded")
        messages.info(
            request,
            "You can find your uploads on your profile page. Files will be parsed and added to the archive when possible. Thanks.",  # noqa: E501
        )
        return HttpResponse(content=template.render(context={}, request=request))


class DeleteUploadView(LoginRequiredMixin, View):
    """Delete an uploaded file."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Delete an uploaded file."""
        file_id: str | None = request.POST.get("file_id", None)
        if not file_id:
            return HttpResponse("No file_id provided", status=400)

        user_file: UserUploadedFile | None = UserUploadedFile.objects.filter(user=request.user, id=file_id).first()
        if not user_file:
            msg = "File not found"
            raise Http404(msg)

        user_upload_dir: Path = Path(settings.MEDIA_ROOT) / "uploads" / f"{request.user.id}"  # type: ignore  # noqa: PGH003
        file_path: Path = user_upload_dir / Path(user_file.file.name).name
        logger.debug("file_path: %s", file_path)

        if not file_path.exists() or not file_path.is_file():
            logger.error("User '%s' attempted to delete a file that does not exist: %s", request.user, file_path)
            msg = "File not found"
            raise Http404(msg)

        if user_upload_dir not in file_path.parents:
            logger.error(
                "User '%s' attempted to delete a file that is not in their upload directory: %s",
                request.user,
                file_path,
            )
            msg = "Attempted unauthorized file access"
            raise SuspiciousOperation(msg)

        user_file.delete()

        # Go back to the profile page
        messages.success(request, f"{file_path.name} deleted")
        return HttpResponse(status=204)


class EditDescriptionView(LoginRequiredMixin, View):
    """Edit the description of an uploaded file."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Edit the description of an uploaded file."""
        new_description: str | None = request.POST.get("description", None)
        file_id: str | None = request.POST.get("file_id", None)
        if not new_description:
            return HttpResponse("No description provided", status=400)
        if not file_id:
            return HttpResponse("No file_id provided", status=400)

        user_file: UserUploadedFile | None = UserUploadedFile.objects.filter(user=request.user, id=file_id).first()
        if not user_file:
            msg = "File not found"
            raise Http404(msg)

        user_upload_dir: Path = Path(settings.MEDIA_ROOT) / "uploads" / f"{request.user.id}"  # type: ignore  # noqa: PGH003
        file_path: Path = user_upload_dir / Path(user_file.file.name).name
        logger.debug("file_path: %s", file_path)

        if not file_path.exists() or not file_path.is_file():
            logger.error("User '%s' attempted to delete a file that does not exist: %s", request.user, file_path)
            msg = "File not found"
            raise Http404(msg)

        if user_upload_dir not in file_path.parents:
            logger.error(
                "User '%s' attempted to delete a file that is not in their upload directory: %s",
                request.user,
                file_path,
            )
            msg = "Attempted unauthorized file access"
            raise SuspiciousOperation(msg)

        old_description: str = user_file.description
        user_file.description = new_description
        user_file.save()

        logger.info(
            "User '%s' updated the description of file '%s' from '%s' to '%s'",
            request.user,
            file_path,
            old_description,
            new_description,
        )
        return HttpResponse(content=new_description, status=200)


class DownloadView(LoginRequiredMixin, View):
    """Download a file."""

    def get(self, request: HttpRequest) -> HttpResponse | FileResponse:
        """/download/?file_id=1."""
        file_id: str | None = request.GET.get("file_id", None)

        if not file_id:
            return HttpResponse("No file_id provided", status=400)

        user_file: UserUploadedFile | None = UserUploadedFile.objects.filter(user=request.user, id=file_id).first()
        if not user_file:
            msg = "File not found"
            raise Http404(msg)

        user_upload_dir: Path = Path(settings.MEDIA_ROOT) / "uploads" / f"{request.user.id}"  # type: ignore  # noqa: PGH003
        file_path: Path = user_upload_dir / Path(user_file.file.name).name

        if not file_path.exists() or not file_path.is_file():
            msg = "File not found"
            raise Http404(msg)

        if user_upload_dir not in file_path.parents:
            msg = "Attempted unauthorized file access"
            raise SuspiciousOperation(msg)

        content_type, _ = guess_type(file_path)
        response = FileResponse(file_path.open("rb"), content_type=content_type or "application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{user_file.original_filename or file_path.name}"'

        return response


class CustomLoginView(LoginView):
    """Custom login view."""

    template_name = "accounts/login.html"
    next_page = reverse_lazy("index")

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        """Check if the form is valid."""
        user: User = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class RegisterView(CreateView):
    """Register view."""

    template_name = "accounts/register.html"
    form_class = UserCreationForm
    success_url: str = reverse_lazy("login")
    extra_context: ClassVar[dict[str, str]] = {
        "title": "Register",
        "description": "Register a new account",
        "keywords": "register, account",
        "author": "TheLovinator",
        "canonical": "https://feedvault.se/accounts/register/",
    }


class CustomLogoutView(LogoutView):
    """Logout view."""

    next_page = reverse_lazy("login")
    extra_context: ClassVar[dict[str, str]] = {
        "title": "Logout",
        "description": "Logout of your account",
        "keywords": "logout, account",
        "author": "TheLovinator",
        "canonical": "https://feedvault.se/accounts/logout/",
    }


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """Custom password change view."""

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("index")
    success_message = "Your password was successfully updated!"
    extra_context: ClassVar[dict[str, str]] = {
        "title": "Change password",
        "description": "Change your password",
        "keywords": "change, password, account",
        "author": "TheLovinator",
        "canonical": "https://feedvault.se/accounts/change-password/",
    }


class ProfileView(LoginRequiredMixin, View):
    """Profile page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Load the profile page."""
        template = loader.get_template(template_name="accounts/profile.html")

        # TODO(TheLovinator): Use htmx to load the feeds and uploads  # noqa: TD003
        user_feeds: BaseManager[Feed] = Feed.objects.filter(user=request.user).order_by("-created_at")[:100]
        user_uploads: BaseManager[UserUploadedFile] = UserUploadedFile.objects.filter(user=request.user).order_by(
            "-created_at",
        )[:100]

        context: dict[str, str | Any] = {
            "description": f"Profile page for {request.user.get_username()}",
            "keywords": f"profile, account, {request.user.get_username()}",
            "author": f"{request.user.get_username()}",
            "canonical": "https://feedvault.se/accounts/profile/",
            "title": f"{request.user.get_username()}",
            "user_feeds": user_feeds,
            "user_uploads": user_uploads,
        }
        return HttpResponse(content=template.render(context=context, request=request))


class RobotsView(View):
    """Robots.txt view."""

    def get(self, request: HttpRequest) -> HttpResponse:  # noqa: ARG002
        """Load the robots.txt file."""
        return HttpResponse(
            content="User-agent: *\nDisallow: /add\nDisallow: /upload\nDisallow: /accounts/\n\nSitemap: https://feedvault.se/sitemap.xml",
            content_type="text/plain",
        )


class DomainsView(View):
    """All domains."""

    def get(self: DomainsView, request: HtmxHttpRequest) -> HttpResponse:
        """Load the domains page."""
        domains: BaseManager[Domain] = Domain.objects.only("id", "url", "created_at")

        paginator = Paginator(object_list=domains, per_page=100)
        page_number = int(request.GET.get("page", default=1))

        try:
            pages: Page = paginator.get_page(page_number)
        except EmptyPage:
            return HttpResponse("")

        context: dict[str, str | Page | int] = {
            "domains": pages,
            "description": "Domains",
            "keywords": "feed, rss, atom, archive, rss list",
            "author": "TheLovinator",
            "canonical": "https://feedvault.se/domains/",
            "title": "Domains",
            "page": page_number,
        }

        template_name = "partials/domains.html" if request.htmx else "domains.html"
        return render(request, template_name, context)


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
