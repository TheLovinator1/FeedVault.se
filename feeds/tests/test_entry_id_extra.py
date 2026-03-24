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
def test_entry_id_id_dict(tmp_path: Path) -> None:
    """Test that entry_id is a string when id is a dict."""
    feed_content = """
    <feed xmlns='http://www.w3.org/2005/Atom'>
      <title>Test Atom Feed</title>
      <id>http://example.com/feed</id>
      <entry>
        <title>Entry 1</title>
        <id scheme='urn:uuid'>urn:uuid:1234</id>
        <link href='http://example.com/entry1'/>
      </entry>
    </feed>
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
    assert "urn:uuid:1234" in entry.entry_id
    server.shutdown()


@pytest.mark.django_db
def test_entry_id_all_fields_missing(tmp_path: Path) -> None:
    """Test that entry_id falls back to content_hash if guid/id/link missing."""
    feed_content = """
    <rss version='2.0'>
      <channel>
        <title>Test Feed</title>
        <item>
          <title>Item with no id</title>
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

    # Should be a hash string (digits only)
    assert entry.entry_id.isdigit() or entry.entry_id.lstrip("-").isdigit()
    server.shutdown()


@pytest.mark.django_db
def test_entry_id_malformed_guid(tmp_path: Path) -> None:
    """Test that entry_id handles malformed guid/id gracefully."""
    feed_content = """
    <rss version='2.0'>
      <channel>
        <title>Test Feed</title>
        <item>
          <title>Malformed guid</title>
          <guid></guid>
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

    # Should fallback to content_hash
    assert entry.entry_id.isdigit() or entry.entry_id.lstrip("-").isdigit()
    server.shutdown()
