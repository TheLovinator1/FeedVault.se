"""Validate feeds before adding them to the database."""

from __future__ import annotations

import ipaddress
import logging
import re
from urllib.parse import urlparse

import requests
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from feeds.models import Blocklist

BLOCKLISTS: list[str] = [
    "https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-dnscrypt-blocked-names.txt",
    "https://malware-filter.gitlab.io/malware-filter/phishing-filter-dnscrypt-blocked-names.txt",
]

logger: logging.Logger = logging.getLogger(__name__)


def validate_scheme(feed_url: str) -> bool:
    """Validate the scheme of a URL. Only allow http and https.

    Args:
        feed_url: The URL to validate.

    Returns:
        True if the URL is valid, False otherwise.
    """
    validator = URLValidator(schemes=["http", "https"])
    # TODO(TheLovinator): Should we allow other schemes?  # noqa: TD003
    try:
        validator(feed_url)
    except ValidationError:
        return False
    else:
        return True


def is_ip(feed_url: str) -> bool:
    """Check if feed is an IP address."""
    try:
        ipaddress.ip_address(feed_url)
    except ValueError:
        logger.info(f"{feed_url} is not an IP address")  # noqa: G004
        return False
    else:
        logger.info(f"{feed_url} is an IP address")  # noqa: G004
        return True


def update_blocklist() -> str:
    """Download the blocklist and add to database."""
    # URLs found in the blocklist
    found_urls = set()

    for _blocklist in BLOCKLISTS:
        with requests.get(url=_blocklist, timeout=10) as r:
            r.raise_for_status()

            logger.debug(f"Downloaded {_blocklist}")  # noqa: G004

            # Split the blocklist into a list of URLs
            blocked_urls = set(r.text.splitlines())

            # Remove comments and whitespace
            blocked_urls = {url for url in blocked_urls if not url.startswith("#")}
            blocked_urls = {url.strip() for url in blocked_urls}

            logger.debug(f"Found {len(blocked_urls)} URLs in {_blocklist}")  # noqa: G004

        # Add URLs to the found URLs set
        found_urls.update(blocked_urls)

        logger.debug(f"Found {len(found_urls)} URLs in total")  # noqa: G004

    # Mark all URLs as inactive
    Blocklist.objects.all().update(active=False)

    logger.debug("Marked all URLs as inactive")

    # Bulk create the blocklist
    Blocklist.objects.bulk_create(
        [Blocklist(url=url, active=True) for url in found_urls],
        update_conflicts=True,
        unique_fields=["url"],
        update_fields=["active"],
        batch_size=1000,
    )

    logger.debug(f"Added {len(found_urls)} URLs to the blocklist")  # noqa: G004
    return f"Added {len(found_urls)} URLs to the blocklist"


def is_local(feed_url: str) -> bool:
    """Check if feed is a local address."""
    # Regexes from https://github.com/gwarser/filter-lists
    regexes: list[str] = [
        # 10.0.0.0 - 10.255.255.255
        r"^\w+:\/\/10\.(?:(?:[1-9]?\d|1\d\d|2(?:[0-4]\d|5[0-5]))\.){2}(?:[1-9]?\d|1\d\d|2(?:[0-4]\d|5[0-5]))[:/]",
        # 172.16.0.0 - 172.31.255.255
        r"^\w+:\/\/172\.(?:1[6-9]|2\d|3[01])(?:\.(?:[1-9]?\d|1\d\d|2(?:[0-4]\d|5[0-5]))){2}[:/]",
        # 192.168.0.0 - 192.168.255.255
        r"^\w+:\/\/192\.168(?:\.(?:[1-9]?\d|1\d\d|2(?:[0-4]\d|5[0-5]))){2}[:/]",
        # https://en.wikipedia.org/wiki/Private_network#Link-local_addresses
        r"^\w+:\/\/169\.254\.(?:[1-9]\d?|1\d{2}|2(?:[0-4]\d|5[0-4]))\.(?:[1-9]?\d|1\d{2}|2(?:[0-4]\d|5[0-5]))[:/]",
        # https://en.wikipedia.org/wiki/IPv6_address#Transition_from_IPv4
        r"^\w+:\/\/\[::ffff:(?:7f[0-9a-f]{2}|a[0-9a-f]{2}|ac1[0-9a-f]|c0a8|a9fe):[0-9a-f]{1,4}\][:/]",
        # localhost
        r"^\w+:\/\/127\.(?:(?:[1-9]?\d|1\d\d|2(?:[0-4]\d|5[0-5]))\.){2}(?:[1-9]?\d|1\d\d|2(?:[0-4]\d|5[0-5]))[:/]",
    ]

    domain: str | None = urlparse(feed_url).hostname
    if not domain:
        return False

    if domain in {"localhost", "127.0.0.1", "::1", "0.0.0.0", "::", "local", "[::1]"}:  # noqa: S104
        return True

    if domain.endswith((".local", ".home.arpa")):
        return True

    return any(re.match(regex, feed_url) for regex in regexes)
