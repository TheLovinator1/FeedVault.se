from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Self

from django.db.models import Q
from reader import ExceptionInfo, FeedExistsError, FeedNotFoundError, Reader, make_reader
from reader._types import (
    EntryForUpdate,  # noqa: PLC2701
    EntryUpdateIntent,
    FeedData,
    FeedFilter,
    FeedForUpdate,  # noqa: PLC2701
    FeedUpdateIntent,
    SearchType,  # noqa: PLC2701
    StorageType,  # noqa: PLC2701
)

from .models import Entry, Feed

if TYPE_CHECKING:
    import datetime

    from django.db.models.manager import BaseManager


logger = logging.getLogger(__name__)


class EmptySearch(SearchType): ...


class EntriesForUpdateIterator:
    def __init__(self, entries: Iterable[tuple[str, str]]) -> None:
        self.entries: Iterator[tuple[str, str]] = iter(entries)

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> EntryForUpdate:
        try:
            feed_url, entry_id = next(self.entries)
        except StopIteration:
            raise StopIteration from None

        print(f"{feed_url=}, {entry_id=}")  # noqa: T201
        entry_data: dict[str, Any] | None = (
            Entry.objects.filter(Q(feed__url=feed_url) & Q(id=entry_id))
            .values("updated", "published", "data_hash", "data_hash_changed")
            .first()
        )

        if not entry_data:
            return None

        return EntryForUpdate(
            updated=entry_data.get("updated"),
            published=entry_data.get("published"),
            hash=entry_data.get("data_hash"),
            hash_changed=entry_data.get("data_hash_changed"),
        )


class DjangoStorage(StorageType):
    # TODO(TheLovinator): Implement all methods from StorageType.
    default_search_cls = EmptySearch

    def __enter__(self: DjangoStorage) -> None:
        """Called when Reader is used as a context manager."""
        # TODO(TheLovinator): Should we check if we have migrations to apply?

    def __exit__(self: DjangoStorage, *_: object) -> None:
        """Called when Reader is used as a context manager."""
        # TODO(TheLovinator): Should we close the connection?

    def close(self: DjangoStorage) -> None:
        """Called by Reader.close()."""
        # TODO(TheLovinator): Should we close the connection?

    def add_feed(self, url: str, /, added: datetime.datetime) -> None:
        """Called by Reader.add_feed().

        Args:
            url: The URL of the feed.
            added: The time the feed was added.

        Raises:
            FeedExistsError: Feed already exists. Bases: FeedError
        """
        if Feed.objects.filter(url=url).exists():
            msg: str = f"Feed already exists: {url}"
            raise FeedExistsError(msg)

        feed = Feed(url=url, added=added)
        feed.save()

    def get_feeds_for_update(self, filter: FeedFilter):  # noqa: A002
        """Called by update logic.

        Args:
            filter: The filter to apply.

        Returns:
            A lazy iterable.
        """
        logger.debug(f"{filter=}")  # noqa: G004
        feeds: BaseManager[Feed] = Feed.objects.all()  # TODO(TheLovinator): Don't get all values, use filter.

        for feed in feeds:
            yield FeedForUpdate(
                url=feed.url,
                updated=feed.updated,
                http_etag=feed.http_etag,
                http_last_modified=feed.http_last_modified,
                stale=feed.stale,
                last_updated=feed.last_updated,
                last_exception=bool(feed.last_exception_type_name),
                hash=feed.data_hash,
            )

    def update_feed(self, intent: FeedUpdateIntent, /) -> None:
        """Called by update logic.

        Args:
            intent: Data to be passed to Storage when updating a feed.

        Raises:
            FeedNotFoundError

        """
        feed: Feed = Feed.objects.get(url=intent.url)
        if feed is None:
            msg: str = f"Feed not found: {intent.url}"
            raise FeedNotFoundError(msg)

        feed.last_updated = intent.last_updated
        feed.http_etag = intent.http_etag
        feed.http_last_modified = intent.http_last_modified

        feed_data: FeedData | None = intent.feed
        if feed_data is not None:
            feed.title = feed_data.title
            feed.link = feed_data.link
            feed.author = feed_data.author
            feed.subtitle = feed_data.subtitle
            feed.version = feed_data.version

        if intent.last_exception is not None:
            last_exception: ExceptionInfo = intent.last_exception
            feed.last_exception_type_name = last_exception.type_name
            feed.last_exception_value = last_exception.value_str
            feed.last_exception_traceback = last_exception.traceback_str

        feed.save()

    def set_feed_stale(self, url: str, stale: bool, /) -> None:  # noqa: FBT001
        """Used by update logic tests.

        Args:
            url: The URL of the feed.
            stale: Whether the next update should update all entries, regardless of their hash or updated.

        Raises:
            FeedNotFoundError
        """
        feed: Feed = Feed.objects.get(url=url)
        if feed is None:
            msg: str = f"Feed not found: {url}"
            raise FeedNotFoundError(msg)

        feed.stale = stale
        feed.save()

    def get_entries_for_update(self, entries: Iterable[tuple[str, str]], /) -> EntriesForUpdateIterator:
        for feed_url, entry_id in entries:
            logger.debug(f"{feed_url=}, {entry_id=}")  # noqa: G004

        entries_list = list(entries)
        print(f"{entries_list=}")  # noqa: T201
        return EntriesForUpdateIterator(entries)

    def add_or_update_entries(self, intents: Iterable[EntryUpdateIntent], /) -> None:
        """Called by update logic.

        Args:
            intents: Data to be passed to Storage when updating a feed.

        Raises:
            FeedNotFoundError
        """
        msg = "Not implemented yet."
        raise NotImplementedError(msg)
        for intent in intents:
            feed_id, entry_id = intent.entry.resource_id
            logger.debug(f"{feed_id=}, {entry_id=}")  # noqa: G004
            # TODO(TheLovinator): Implement this method. Use Entry.objects.get_or_create()/Entry.objects.bulk_create()?
            # TODO(TheLovinator): Raise FeedNotFoundError if feed does not exist.

    def make_search(self) -> SearchType:
        """Called by Reader.make_search().

        Returns:
            A Search instance.
        """
        return EmptySearch()


@lru_cache(maxsize=1)
def get_reader() -> Reader:
    """Create a Reader instance.

    reader = get_reader()
    reader.add_feed("https://example.com/feed", added=datetime.datetime.now())
    reader.update_feeds()

    Returns:
        A Reader instance.
    """
    return make_reader(
        "",
        _storage=DjangoStorage(),
        search_enabled=False,
    )
