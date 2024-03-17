from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

import dateparser
import feedparser
from django.utils import timezone
from feedparser import FeedParserDict

from feedvault.models import Author, Domain, Entry, Feed, FeedAddResult, Generator, Publisher

if TYPE_CHECKING:
    import datetime

    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

logger: logging.Logger = logging.getLogger(__name__)


def get_domain(url: str | None) -> None | str:
    """Get the domain of a URL."""
    if not url:
        return None

    # Parse the URL.
    parsed_url: ParseResult = urlparse(url)
    if not parsed_url:
        logger.error("Error parsing URL: %s", url)
        return None

    # Get the domain.
    return str(parsed_url.netloc)


def get_author(parsed_feed: dict) -> Author:
    """Get the author of a feed.

    Args:
        parsed_feed: The parsed feed.

    Returns:
        The author of the feed. If the author doesn't exist, it will be created.
    """
    # A dictionary with details about the author of this entry.
    author_detail: dict = parsed_feed.get("author_detail", {})
    author = Author(
        name=author_detail.get("name", ""),
        href=author_detail.get("href", ""),
        email=author_detail.get("email", ""),
    )

    # Create the author if it doesn't exist.
    try:
        author: Author = Author.objects.get(name=author.name, email=author.email, href=author.href)
    except Author.DoesNotExist:
        author.save()
        logger.info("Created author: %s", author)

    return author


def def_generator(parsed_feed: dict) -> Generator:
    """Get the generator of a feed.

    Args:
        parsed_feed: The parsed feed.

    Returns:
        The generator of the feed. If the generator doesn't exist, it will be created.
    """
    generator_detail: dict = parsed_feed.get("generator_detail", {})
    generator = Generator(
        name=generator_detail.get("name", ""),
        href=generator_detail.get("href", ""),
        version=generator_detail.get("version", ""),
    )

    # Create the generator if it doesn't exist.
    try:
        generator: Generator = Generator.objects.get(
            name=generator.name,
            href=generator.href,
            version=generator.version,
        )
    except Generator.DoesNotExist:
        generator.save()
        logger.info("Created generator: %s", generator)

    return generator


def get_publisher(parsed_feed: dict) -> Publisher:
    """Get the publisher of a feed.

    Args:
        parsed_feed: The parsed feed.

    Returns:
        The publisher of the feed. If the publisher doesn't exist, it will be created.
    """
    publisher_detail: dict = parsed_feed.get("publisher_detail", {})
    publisher = Publisher(
        name=publisher_detail.get("name", ""),
        href=publisher_detail.get("href", ""),
        email=publisher_detail.get("email", ""),
    )

    # Create the publisher if it doesn't exist.
    try:
        publisher: Publisher = Publisher.objects.get(
            name=publisher.name,
            href=publisher.href,
            email=publisher.email,
        )
    except Publisher.DoesNotExist:
        publisher.save()
        logger.info("Created publisher: %s", publisher)

    return publisher


def parse_feed(url: str | None) -> dict | None:
    """Parse a feed.

    Args:
        url: The URL of the feed.

    Returns:
        The parsed feed.
    """
    # TODO(TheLovinator): Backup the feed URL.  # noqa: TD003
    if not url:
        return None

    # Parse the feed.
    parsed_feed: dict = feedparser.parse(url)
    if not parsed_feed:
        return None

    return parsed_feed


def add_entry(feed: Feed, entry: FeedParserDict) -> Entry | None:
    """Add an entry to the database.

    Args:
        entry: The entry to add.
        feed: The feed the entry belongs to.
    """
    author: Author = get_author(parsed_feed=entry)
    publisher: Publisher = get_publisher(parsed_feed=entry)
    pre_updated_parsed: str = str(entry.get("updated_parsed", ""))
    updated_parsed: datetime.datetime | None = (
        dateparser.parse(date_string=str(pre_updated_parsed)) if pre_updated_parsed else None
    )

    pre_published_parsed: str = str(entry.get("published_parsed", ""))
    published_parsed: datetime.datetime | None = (
        dateparser.parse(date_string=str(pre_published_parsed)) if pre_published_parsed else None
    )

    pre_expired_parsed: str = str(entry.get("expired_parsed", ""))
    expired_parsed: datetime.datetime | None = (
        dateparser.parse(date_string=str(pre_expired_parsed)) if pre_expired_parsed else None
    )

    pre_created_parsed = str(entry.get("created_parsed", ""))
    created_parsed: datetime.datetime | None = (
        dateparser.parse(date_string=str(pre_created_parsed)) if pre_created_parsed else None
    )

    entry_id = entry.get("id", "")
    if not entry_id:
        logger.error("Entry ID not found: %s", entry)

    added_entry, created = Entry.objects.update_or_create(
        feed=feed,
        entry_id=entry_id,
        defaults={
            "author": entry.get("author", ""),
            "author_detail": author,
            "comments": entry.get("comments", ""),
            "content": entry.get("content", {}),
            "contributors": entry.get("contributors", {}),
            "created": entry.get("created", ""),
            "created_parsed": created_parsed,
            "enclosures": entry.get("enclosures", []),
            "expired": entry.get("expired", ""),
            "expired_parsed": expired_parsed,
            "license": entry.get("license", ""),
            "link": entry.get("link", ""),
            "links": entry.get("links", []),
            "published": entry.get("published", ""),
            "published_parsed": published_parsed,
            "publisher": entry.get("publisher", ""),
            "publisher_detail": publisher,
            "source": entry.get("source", {}),
            "summary": entry.get("summary", ""),
            "summary_detail": entry.get("summary_detail", {}),
            "tags": entry.get("tags", []),
            "title": entry.get("title", ""),
            "title_detail": entry.get("title_detail", {}),
            "updated": entry.get("updated", ""),
            "updated_parsed": updated_parsed,
        },
    )
    if created:
        logger.info("Created entry: %s", added_entry)
        return added_entry

    logger.info("Updated entry: %s", added_entry)
    return added_entry


def add_domain_to_db(url: str | None) -> Domain | None:
    """Add a domain to the database.

    Args:
        url: The URL of the domain.

    Returns:
        The domain that was added.
    """
    domain_url: None | str = get_domain(url=url)
    if not domain_url:
        return None

    # Create the domain if it doesn't exist.
    domain: Domain
    domain, created = Domain.objects.get_or_create(url=domain_url)
    if created:
        logger.info("Created domain: %s", domain.url)
        domain.save()

    return domain


def populate_feed(url: str | None, user: AbstractBaseUser | AnonymousUser) -> Feed | None:
    """Populate the feed with entries.

    Args:
        url: The URL of the feed.
        user: The user adding the feed.

    Returns:
        The feed that was added.
    """
    domain: Domain | None = add_domain_to_db(url=url)
    if not domain:
        return None

    # Parse the feed.
    parsed_feed: dict | None = parse_feed(url=url)
    if not parsed_feed:
        return None

    author: Author = get_author(parsed_feed=parsed_feed)
    generator: Generator = def_generator(parsed_feed=parsed_feed)
    publisher: Publisher = get_publisher(parsed_feed=parsed_feed)

    pre_published_parsed: str = str(parsed_feed.get("published_parsed", ""))
    published_parsed: datetime.datetime | None = (
        dateparser.parse(date_string=str(pre_published_parsed)) if pre_published_parsed else None
    )

    pre_updated_parsed: str = str(parsed_feed.get("updated_parsed", ""))
    updated_parsed: datetime.datetime | None = (
        dateparser.parse(date_string=str(pre_updated_parsed)) if pre_updated_parsed else None
    )

    pre_modified: str = str(parsed_feed.get("modified", ""))
    modified: timezone.datetime | None = dateparser.parse(date_string=pre_modified) if pre_modified else None

    # Create or update the feed
    feed, created = Feed.objects.update_or_create(
        feed_url=url,
        domain=domain,
        defaults={
            "user": user,
            "last_checked": timezone.now(),
            "bozo": parsed_feed.get("bozo", 0),
            "bozo_exception": parsed_feed.get("bozo_exception", ""),
            "encoding": parsed_feed.get("encoding", ""),
            "etag": parsed_feed.get("etag", ""),
            "headers": parsed_feed.get("headers", {}),
            "href": parsed_feed.get("href", ""),
            "modified": modified,
            "namespaces": parsed_feed.get("namespaces", {}),
            "status": parsed_feed.get("status", 0),
            "version": parsed_feed.get("version", ""),
            "author": parsed_feed.get("author", ""),
            "author_detail": author,
            "cloud": parsed_feed.get("cloud", {}),
            "contributors": parsed_feed.get("contributors", {}),
            "docs": parsed_feed.get("docs", ""),
            "errorreportsto": parsed_feed.get("errorreportsto", ""),
            "generator": parsed_feed.get("generator", ""),
            "generator_detail": generator,
            "icon": parsed_feed.get("icon", ""),
            "feed_id": parsed_feed.get("id", ""),
            "image": parsed_feed.get("image", {}),
            "info": parsed_feed.get("info", ""),
            "language": parsed_feed.get("language", ""),
            "license": parsed_feed.get("license", ""),
            "link": parsed_feed.get("link", ""),
            "links": parsed_feed.get("links", []),
            "logo": parsed_feed.get("logo", ""),
            "published": parsed_feed.get("published", ""),
            "published_parsed": published_parsed,
            "publisher": parsed_feed.get("publisher", ""),
            "publisher_detail": publisher,
            "rights": parsed_feed.get("rights", ""),
            "rights_detail": parsed_feed.get("rights_detail", {}),
            "subtitle": parsed_feed.get("subtitle", ""),
            "subtitle_detail": parsed_feed.get("subtitle_detail", {}),
            "tags": parsed_feed.get("tags", []),
            "textinput": parsed_feed.get("textinput", {}),
            "title": parsed_feed.get("title", ""),
            "title_detail": parsed_feed.get("title_detail", {}),
            "ttl": parsed_feed.get("ttl", ""),
            "updated": parsed_feed.get("updated", ""),
            "updated_parsed": updated_parsed,
        },
    )

    grab_entries(feed=feed)

    if created:
        logger.info("Created feed: %s", feed)
        return feed

    logger.info("Updated feed: %s", feed)
    return feed


def grab_entries(feed: Feed) -> None | list[Entry]:
    """Grab the entries from a feed.

    Args:
        feed: The feed to grab the entries from.

    Returns:
        The entries that were added. If no entries were added, None is returned.
    """
    # Set the last checked time to now.
    feed.last_checked = timezone.now()
    feed.save()

    entries_added: list[Entry] = []
    # Parse the feed.
    parsed_feed: dict | None = parse_feed(url=feed.feed_url)
    if not parsed_feed:
        return None

    entries = parsed_feed.get("entries", [])
    for entry in entries:
        added_entry: Entry | None = add_entry(feed=feed, entry=entry)
        if not added_entry:
            continue
        entries_added.append(added_entry)

    logger.info("Added entries: %s", entries_added)
    return entries_added


def add_url(url: str, user: AbstractBaseUser | AnonymousUser) -> FeedAddResult:
    """Add a feed to the database so we can grab entries from it later."""
    domain: Domain | None = add_domain_to_db(url=url)
    if not domain:
        return FeedAddResult(feed=None, created=False, error="Domain not found")

    # Add the URL to the database.
    _feed, _created = Feed.objects.get_or_create(feed_url=url, user=user, domain=domain)
    return FeedAddResult(feed=_feed, created=_created, error=None)
