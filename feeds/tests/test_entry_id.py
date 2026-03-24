import os
import threading
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from feeds.models import Entry
from feeds.models import Feed
from feeds.services import fetch_and_archive_feed

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.django_db
def test_entry_id_string_guid_dict(tmp_path: Path) -> None:
    """Test that entry_id is always a string, even if guid is a dict."""
    # Prepare a fake RSS feed with guid as dict (attributes)
    feed_content = """
    <rss version="2.0">
      <channel>
        <title>Test Feed</title>
        <link>http://example.com/</link>
        <description>Test feed description</description>
        <item>
          <title>Item 1</title>
          <link>http://example.com/item1</link>
          <guid isPermaLink="true">http://example.com/item1</guid>
        </item>
      </channel>
    </rss>
    """
    feed_path: Path = tmp_path / "test_feed.xml"
    feed_path.write_text(feed_content, encoding="utf-8")
    os.chdir(tmp_path)
    server = HTTPServer(("localhost", 0), SimpleHTTPRequestHandler)
    port: int = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url: str = f"http://localhost:{port}/test_feed.xml"
    feed: Feed = Feed.objects.create(url=url, domain="localhost")
    fetch_and_archive_feed(feed)
    entry: Entry | None = Entry.objects.filter(feed=feed).first()
    assert entry is not None
    assert isinstance(entry.entry_id, str)
    assert entry.entry_id == "http://example.com/item1"
    server.shutdown()


@pytest.mark.django_db
def test_entry_id_string_guid_string(tmp_path: Path) -> None:
    """Test that entry_id is a string when guid is a plain string."""
    feed_content = """
    <rss version="2.0">
      <channel>
        <title>Test Feed</title>
        <link>http://example.com/</link>
        <description>Test feed description</description>
        <item>
          <title>Item 2</title>
          <link>http://example.com/item2</link>
          <guid>http://example.com/item2</guid>
        </item>
      </channel>
    </rss>
    """
    feed_path: Path = tmp_path / "test_feed.xml"
    feed_path.write_text(feed_content, encoding="utf-8")
    os.chdir(tmp_path)
    server = HTTPServer(("localhost", 0), SimpleHTTPRequestHandler)
    port: int = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url: str = f"http://localhost:{port}/test_feed.xml"
    feed: Feed = Feed.objects.create(url=url, domain="localhost")
    fetch_and_archive_feed(feed)
    entry: Entry | None = Entry.objects.filter(feed=feed).first()
    assert entry is not None
    assert isinstance(entry.entry_id, str)
    assert entry.entry_id == "http://example.com/item2"
    server.shutdown()


@pytest.mark.django_db
def test_entry_id_fallback_to_link(tmp_path: Path) -> None:
    """Test that entry_id falls back to link if guid/id missing."""
    feed_content = """
    <rss version="2.0">
      <channel>
        <title>Test Feed</title>
        <link>http://example.com/</link>
        <description>Test feed description</description>
        <item>
          <title>Item 3</title>
          <link>http://example.com/item3</link>
        </item>
      </channel>
    </rss>
    """
    feed_path: Path = tmp_path / "test_feed.xml"
    feed_path.write_text(feed_content, encoding="utf-8")
    os.chdir(tmp_path)
    server = HTTPServer(("localhost", 0), SimpleHTTPRequestHandler)
    port: int = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url: str = f"http://localhost:{port}/test_feed.xml"
    feed: Feed = Feed.objects.create(url=url, domain="localhost")
    fetch_and_archive_feed(feed)
    entry: Entry | None = Entry.objects.filter(feed=feed).first()
    assert entry is not None
    assert isinstance(entry.entry_id, str)
    assert entry.entry_id == "http://example.com/item3"
    server.shutdown()
