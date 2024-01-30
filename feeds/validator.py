"""Validate feeds before adding them to the database."""

from __future__ import annotations

import ipaddress
import logging
import socket
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
        logger.info(f"{feed_url} passed isn't either a v4 or a v6 address")  # noqa: G004
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
    network_location: str = urlparse(url=feed_url).netloc

    # Check if network location is an IP address
    if is_ip(feed_url=network_location):
        try:
            ip: ipaddress.IPv4Address | ipaddress.IPv6Address = ipaddress.ip_address(address=network_location)
        except ValueError:
            return False
        else:
            return ip.is_private

    try:
        ip_address: str = socket.gethostbyname(network_location)
        is_private: bool = ipaddress.ip_address(address=ip_address).is_private
    except socket.gaierror as e:
        logger.info(f"{feed_url} failed to resolve: {e}")  # noqa: G004
        return True
    except ValueError as e:
        logger.info(f"{feed_url} failed to resolve: {e}")  # noqa: G004
        return True

    msg: str = f"{feed_url} is a local URL" if is_private else f"{feed_url} is not a local URL"
    logger.info(msg)

    return is_private
