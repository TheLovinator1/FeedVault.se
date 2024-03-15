from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from feedvault.models import Domain, Entry, Feed

if TYPE_CHECKING:
    from django.http import HttpResponse


class TestIndexPage(TestCase):
    def test_index_page(self) -> None:
        """Test if the index page is accessible."""
        response: HttpResponse = self.client.get(reverse("index"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response: HttpResponse = self.client.get("/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestFeedPage(TestCase):
    def setUp(self) -> None:
        """Create a test feed."""
        self.domain: Domain = Domain.objects.create(
            name="feedvault",
            url="feedvault.se",
        )

        self.user: User = User.objects.create_user(
            username="testuser",
            email="hello@feedvault.se",
            password="testpassword",  # noqa: S106
        )
        self.feed: Feed = Feed.objects.create(
            user=self.user,
            bozo=False,
            feed_url="https://feedvault.se/feed.xml",
            domain=self.domain,
        )

    def test_feed_page(self) -> None:
        """Test if the feed page is accessible."""
        response: HttpResponse = self.client.get(reverse("feed", kwargs={"feed_id": 1}))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_feed_page_not_found(self) -> None:
        """Test if the feed page is accessible."""
        response: HttpResponse = self.client.get(reverse("feed", kwargs={"feed_id": 2}))
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestFeedsPage(TestCase):
    def test_feeds_page(self) -> None:
        """Test if the feeds page is accessible."""
        response: HttpResponse = self.client.get(reverse("feeds"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestAddPage(TestCase):
    def test_add_page(self) -> None:
        """Test if the add page is accessible."""
        response: HttpResponse = self.client.get(reverse("add"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestUploadPage(TestCase):
    def test_upload_page(self) -> None:
        """Test if the upload page is accessible."""
        response: HttpResponse = self.client.get(reverse("upload"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestRobotsPage(TestCase):
    def test_robots_page(self) -> None:
        """Test if the robots page is accessible."""
        response: HttpResponse = self.client.get(reverse("robots"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_robots_page_content(self) -> None:
        """Test if the robots page contains the expected content."""
        response: HttpResponse = self.client.get(reverse("robots"))
        assert (
            response.content == b"User-agent: *\nDisallow: /add\nDisallow: /upload\nDisallow: /accounts/"
        ), f"Expected b'User-agent: *\nDisallow: /add\nDisallow: /upload\nDisallow: /accounts/', got {response.content}"


class TestDomains(TestCase):
    def test_domains_page(self) -> None:
        """Test if the domains page is accessible."""
        response: HttpResponse = self.client.get(reverse("domains"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestAPI(TestCase):
    def test_api_page(self) -> None:
        """Test if the API page is accessible."""
        response: HttpResponse = self.client.get(reverse("api_v1:openapi-view"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestAPIFeeds(TestCase):
    def test_api_feeds_page(self) -> None:
        """Test if the API feeds page is accessible."""
        response: HttpResponse = self.client.get(reverse("api_v1:list_feeds"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class FeedVaultAPITests(TestCase):
    def setUp(self) -> None:
        # Set up data for the whole TestCase
        self.client = Client()

        # Creating a domain instance
        self.domain: Domain = Domain.objects.create(name="Example Domain")

        # Creating a feed instance
        self.feed: Feed = Feed.objects.create(title="Example Feed", domain=self.domain, bozo=False)

        # Creating entry instances
        self.entry1: Entry = Entry.objects.create(title="Example Entry 1", feed=self.feed)
        self.entry2: Entry = Entry.objects.create(title="Example Entry 2", feed=self.feed)

    def test_list_feeds(self) -> None:
        response: HttpResponse = self.client.get("/api/v1/feeds/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Example Feed" in response.content.decode()

    def test_get_feed(self) -> None:
        response: HttpResponse = self.client.get(f"/api/v1/feeds/{self.feed.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Example Feed" in response.content.decode()

    def test_list_entries(self) -> None:
        response: HttpResponse = self.client.get(f"/api/v1/feeds/{self.feed.pk}/entries/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Example Entry 1" in response.content.decode()
        assert "Example Entry 2" in response.content.decode()

    def test_get_entry(self) -> None:
        response: HttpResponse = self.client.get(f"/api/v1/entries/{self.entry1.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Example Entry 1" in response.content.decode()

    def test_list_domains(self) -> None:
        response: HttpResponse = self.client.get("/api/v1/domains/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Example Domain" in response.content.decode()

    def test_get_domain(self) -> None:
        response: HttpResponse = self.client.get(f"/api/v1/domains/{self.domain.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Example Domain" in response.content.decode()


class TestAccount(TestCase):
    def test_login_page(self) -> None:
        """Test if the login page is accessible."""
        response: HttpResponse = self.client.get(reverse("login"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_register_page(self) -> None:
        """Test if the register page is accessible."""
        response: HttpResponse = self.client.get(reverse("register"))
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestLogoutPage(TestCase):
    def setUp(self) -> None:
        """Create a test user."""
        self.user: User = User.objects.create_user(
            username="testuser",
            email="hello@feedvault.se",
            password="testpassword",  # noqa: S106
        )

        self.client.force_login(user=self.user)

    def test_logout_page(self) -> None:
        """Test if the logout page is accessible."""
        response: HttpResponse = self.client.post(reverse("logout"))
        assert response.status_code == 302, f"Expected 300, got {response.status_code}"

        # Check if the user is logged out
        response: HttpResponse = self.client.get(reverse("index"))
        assert response.status_code == 200
        assert "testuser" not in response.content.decode("utf-8")
