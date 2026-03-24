from typing import TYPE_CHECKING
from typing import Any
from xml.parsers.expat import ExpatError

import dateparser
import niquests
import xmltodict
import xxhash
from django.conf import settings
from django.utils import timezone

from feeds.models import Entry

if TYPE_CHECKING:
    import datetime

    from feeds.models import Feed

HTTP_OK = 200
HTTP_NOT_MODIFIED = 304


def extract_id(val: str | dict | None) -> str | None:
    """Extracts a string ID from a guid or id field, handling both string and dict formats.

    Args:
        val (str | dict | None): The value to extract the ID from, which can be a string, a dict (with possible '#text' or '@id' keys), or None

    Returns:
        str | None: The extracted ID as a string, or None if it cannot be extracted
    """
    if isinstance(val, dict):
        # RSS guid or Atom id as dict: prefer '#text', fallback to str(val)
        return val.get("#text") or val.get("@id") or str(val)
    return val


def fetch_and_archive_feed(feed: Feed) -> int:
    """Fetches the feed, parses entries, deduplicates, and archives new entries.

    Returns:
        The number of new entries archived.
    """
    request_headers: dict[str, str] = get_request_headers()
    if feed.etag:
        request_headers["If-None-Match"] = feed.etag
    if feed.last_modified:
        request_headers["If-Modified-Since"] = feed.last_modified

    try:
        response: niquests.Response = niquests.get(
            feed.url,
            headers=request_headers,
            timeout=10,
        )

        if response.status_code == HTTP_NOT_MODIFIED:
            feed.last_fetched_at = timezone.now()
            feed.save(update_fields=["last_fetched_at"])
            return 0

        raw_xml: bytes = response.content or b""
        error_msg: str = ""
        parsed_data: dict[str, Any] | None = None
        if response.status_code == HTTP_OK:
            try:
                parsed_data = xmltodict.parse(
                    raw_xml.decode("utf-8", errors="replace"),
                    process_namespaces=False,
                )
            except ExpatError as e:
                error_msg = f"XML Parsing Error: {e!s}"

        # Extract entries from parsed_data
        entries: list[dict[str, Any]] = extract_feed_entries(parsed_data)

        new_count = 0
        for entry in entries:
            content_hash: int = calculate_content_hash(entry)

            entry_id: str = (
                extract_id(entry.get("guid"))
                or extract_id(entry.get("id"))
                or entry.get("link")
                or str(content_hash)
            )
            if not isinstance(entry_id, str):
                entry_id = str(entry_id)

            published_at: datetime.datetime | None = None
            for date_field in ("published", "pubDate", "updated", "created"):
                if entry.get(date_field):
                    published_at = dateparser.parse(entry[date_field])
                    if published_at:
                        break

            # Deduplicate: skip if entry with same feed+entry_id+content_hash exists
            exists: bool = Entry.objects.filter(
                feed=feed,
                entry_id=entry_id,
                content_hash=content_hash,
            ).exists()
            if not exists:
                Entry.objects.create(
                    feed=feed,
                    entry_id=entry_id,
                    fetched_at=timezone.now(),
                    published_at=published_at,
                    content_hash=content_hash,
                    data=entry,
                    error_message=error_msg,
                )
                new_count += 1

        feed.etag = response.headers.get("ETag", "")
        feed.last_modified = response.headers.get("Last-Modified", "")
        feed.last_fetched_at = timezone.now()
        feed.save()

    except niquests.exceptions.RequestException as e:
        Entry.objects.create(
            feed=feed,
            entry_id="__error__",
            fetched_at=timezone.now(),
            published_at=None,
            content_hash=0,
            data=None,
            error_message=str(e),
        )
        return 0

    else:
        return new_count


def calculate_content_hash(entry: dict[str, Any]) -> int:
    """Calculates a content hash for the entry using xxhash64.

    Args:
        entry (dict[str, Any]): The entry data as a dictionary.

    Returns:
        int: A 64-bit integer hash of the entry content, suitable for deduplication.
    """
    entry_bytes: bytes = str(entry).encode("utf-8")
    entry_hash_int: int = xxhash.xxh64_intdigest(entry_bytes)

    # Ensure content_hash fits in signed 64-bit integer
    content_hash: int = entry_hash_int & 0x7FFFFFFFFFFFFFFF
    return content_hash


def extract_feed_entries(parsed_data: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Extracts a list of entries from the parsed feed data, handling both RSS and Atom formats.

    Args:
        parsed_data (dict[str, Any] | None): The parsed feed data as a dictionary, or None if parsing failed

    Returns:
        list[dict[str, Any]]: A list of entries extracted from the feed, where each entry is represented as a dictionary. If no entries are found or if parsed_data is None, an empty list is returned.
    """
    entries: list[dict[str, Any]] = []
    if parsed_data:
        # RSS: channel > item; Atom: feed > entry
        items: list[dict[str, Any]] | dict[str, Any] = []
        if "rss" in parsed_data:
            items = parsed_data["rss"].get("channel", {}).get("item", [])
        elif "feed" in parsed_data:
            items = parsed_data["feed"].get("entry", [])
        if isinstance(items, dict):
            items = [items]
        entries = items
    return entries


def get_request_headers() -> dict[str, str]:
    """Helper function to get standard request headers for fetching feeds.

    Returns:
        dict[str, str]: A dictionary of HTTP headers to include in feed fetch requests.
    """
    # https://blog.cloudflare.com/verified-bots-with-cryptography/
    # https://www.cloudflare.com/lp/verified-bots/
    # TODO(TheLovinator): We have to sign our requests  # noqa: TD003

    request_headers: dict[str, str] = {
        "User-Agent": settings.USER_AGENT,
        "From": settings.BOT_CONTACT_EMAIL,
    }

    return request_headers
