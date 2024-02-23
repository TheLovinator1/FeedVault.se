from __future__ import annotations

import datetime
import logging
from time import mktime, struct_time
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

import feedparser
from django.utils import timezone
from feedparser import FeedParserDict

from feeds.models import Author, Domain, Entry, Feed, Generator, Publisher

if TYPE_CHECKING:
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
    # TODO(TheLovinator): Backup the feed URL to a cloudflare worker.  # noqa: TD003
    if not url:
        return None

    # Parse the feed.
    parsed_feed: dict = feedparser.parse(url)
    if not parsed_feed:
        return None

    return parsed_feed


def struct_time_to_datetime(struct_time: struct_time | None) -> datetime.datetime | None:
    """Convert a struct_time to a datetime."""
    if not struct_time:
        return None

    dt: datetime.datetime = datetime.datetime.fromtimestamp(mktime(struct_time), tz=datetime.timezone.utc)
    if not dt:
        logger.error("Error converting struct_time to datetime: %s", struct_time)
        return None
    return dt


def add_entry(feed: Feed, entry: FeedParserDict) -> Entry | None:
    """Add an entry to the database.

    Args:
        entry: The entry to add.
        feed: The feed the entry belongs to.
    """
    author: Author = get_author(parsed_feed=entry)
    publisher: Publisher = get_publisher(parsed_feed=entry)
    updated_parsed: datetime | None = struct_time_to_datetime(struct_time=entry.get("updated_parsed"))  # type: ignore  # noqa: PGH003
    published_parsed: datetime | None = struct_time_to_datetime(struct_time=entry.get("published_parsed"))  # type: ignore  # noqa: PGH003
    expired_parsed: datetime | None = struct_time_to_datetime(struct_time=entry.get("expired_parsed"))  # type: ignore  # noqa: PGH003
    created_parsed: datetime | None = struct_time_to_datetime(struct_time=entry.get("created_parsed"))  # type: ignore  # noqa: PGH003

    _entry = Entry(
        feed=feed,
        author=entry.get("author", ""),
        author_detail=author,
        comments=entry.get("comments", ""),
        content=entry.get("content", {}),
        contributors=entry.get("contributors", {}),
        created=entry.get("created", ""),
        created_parsed=created_parsed,
        enclosures=entry.get("enclosures", []),
        expired=entry.get("expired", ""),
        expired_parsed=expired_parsed,
        _id=entry.get("id", ""),
        license=entry.get("license", ""),
        link=entry.get("link", ""),
        links=entry.get("links", []),
        published=entry.get("published", ""),
        published_parsed=published_parsed,
        publisher=entry.get("publisher", ""),
        publisher_detail=publisher,
        source=entry.get("source", {}),
        summary=entry.get("summary", ""),
        summary_detail=entry.get("summary_detail", {}),
        tags=entry.get("tags", []),
        title=entry.get("title", ""),
        title_detail=entry.get("title_detail", {}),
        updated=entry.get("updated", ""),
        updated_parsed=updated_parsed,
    )

    # Save the entry.
    try:
        _entry.save()
    except Exception:
        logger.exception("Error saving entry for feed: %s", feed)
        return None

    logger.info("Created entry: %s", _entry)

    return _entry


def add_feed(url: str | None, user: AbstractBaseUser | AnonymousUser) -> Feed | None:
    """Add a feed to the database.

    Args:
        url: The URL of the feed.
        user: The user adding the feed.

    Returns:
        The feed that was added.
    """
    # Parse the feed.
    parsed_feed: dict | None = parse_feed(url=url)
    if not parsed_feed:
        return None

    domain_url: None | str = get_domain(url=url)
    if not domain_url:
        return None

    # Create the domain if it doesn't exist.
    domain: Domain
    domain, created = Domain.objects.get_or_create(url=domain_url)
    if created:
        logger.info("Created domain: %s", domain.url)
        domain.save()

    author: Author = get_author(parsed_feed=parsed_feed)
    generator: Generator = def_generator(parsed_feed=parsed_feed)
    publisher: Publisher = get_publisher(parsed_feed=parsed_feed)

    published_parsed: datetime | None = struct_time_to_datetime(struct_time=parsed_feed.get("published_parsed"))  # type: ignore  # noqa: PGH003
    updated_parsed: datetime | None = struct_time_to_datetime(struct_time=parsed_feed.get("updated_parsed"))  # type: ignore  # noqa: PGH003

    # Create the feed
    feed = Feed(
        feed_url=url,
        user=user,
        domain=domain,
        last_checked=timezone.now(),
        bozo=parsed_feed.get("bozo", 0),
        bozo_exception=parsed_feed.get("bozo_exception", ""),
        encoding=parsed_feed.get("encoding", ""),
        etag=parsed_feed.get("etag", ""),
        headers=parsed_feed.get("headers", {}),
        href=parsed_feed.get("href", ""),
        modified=parsed_feed.get("modified"),
        namespaces=parsed_feed.get("namespaces", {}),
        status=parsed_feed.get("status", 0),
        version=parsed_feed.get("version", ""),
        author=parsed_feed.get("author", ""),
        author_detail=author,
        cloud=parsed_feed.get("cloud", {}),
        contributors=parsed_feed.get("contributors", {}),
        docs=parsed_feed.get("docs", ""),
        errorreportsto=parsed_feed.get("errorreportsto", ""),
        generator=parsed_feed.get("generator", ""),
        generator_detail=generator,
        icon=parsed_feed.get("icon", ""),
        _id=parsed_feed.get("id", ""),
        image=parsed_feed.get("image", {}),
        info=parsed_feed.get("info", ""),
        language=parsed_feed.get("language", ""),
        license=parsed_feed.get("license", ""),
        link=parsed_feed.get("link", ""),
        links=parsed_feed.get("links", []),
        logo=parsed_feed.get("logo", ""),
        published=parsed_feed.get("published", ""),
        published_parsed=published_parsed,
        publisher=parsed_feed.get("publisher", ""),
        publisher_detail=publisher,
        rights=parsed_feed.get("rights", ""),
        rights_detail=parsed_feed.get("rights_detail", {}),
        subtitle=parsed_feed.get("subtitle", ""),
        subtitle_detail=parsed_feed.get("subtitle_detail", {}),
        tags=parsed_feed.get("tags", []),
        textinput=parsed_feed.get("textinput", {}),
        title=parsed_feed.get("title", ""),
        title_detail=parsed_feed.get("title_detail", {}),
        ttl=parsed_feed.get("ttl", ""),
        updated=parsed_feed.get("updated", ""),
        updated_parsed=updated_parsed,
    )

    # Save the feed.
    try:
        feed.save()
    except Exception:
        logger.exception("Error saving feed: %s", feed)
        return None

    entries = parsed_feed.get("entries", [])
    for entry in entries:
        added_entry: Entry | None = add_entry(feed=feed, entry=entry)
        if not added_entry:
            continue

    logger.info("Created feed: %s", feed)
    return feed
