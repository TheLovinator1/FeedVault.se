"""https://docs.djangoproject.com/en/5.0/topics/testing/."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from django.test import Client, TestCase

from feeds.validator import is_ip, validate_scheme

if TYPE_CHECKING:
    from django.http import HttpResponse


class TestHomePage(TestCase):
    """Test case for the home page view."""

    def setUp(self: TestHomePage) -> None:
        """Set up the test client for the test case."""
        self.client = Client()

    def test_home_page(self: TestHomePage) -> None:
        """Test that a GET request to the home page returns a 200 status code."""
        response: HttpResponse = self.client.get("/")
        assert response.status_code == 200


class TestValidator(TestCase):
    """Test case for the validator."""

    def setUp(self: TestValidator) -> None:
        """Set up the test client for the test case."""
        self.client = Client()

    def test_is_ip(self: TestValidator) -> None:
        """Test that is_ip() returns True for a valid IP address."""
        # Test random IP address
        random_ip: str = ".".join(str(random.randint(0, 255)) for _ in range(4))  # noqa: S311
        assert is_ip(feed_url=random_ip)

        # Test domain name
        assert not is_ip(feed_url="https://example.com")

    def test_validate_scheme(self: TestValidator) -> None:
        """Test that validate_scheme() returns True for a valid scheme."""
        assert validate_scheme(feed_url="https://example.com")
        assert validate_scheme(feed_url="http://example.com")
        assert not validate_scheme(feed_url="ftp://example.com")
        assert not validate_scheme(feed_url="example.com")
        assert not validate_scheme(feed_url="127.0.0.1")
