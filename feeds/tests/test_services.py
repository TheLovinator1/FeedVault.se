import os
import threading
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from feeds.models import Entry
from feeds.models import Feed
from feeds.services import fetch_and_archive_feed


@pytest.mark.django_db
def test_fetch_and_archive_feed_xml(tmp_path: Path) -> None:
    """Test fetching and archiving a simple XML feed using a local HTTP server."""
    # Use a local test XML file as a feed source
    test_feed_path: Path = tmp_path / "test_feed.xml"
    test_feed_path.write_text(
        encoding="utf-8",
        data="""
        <rss version='2.0'>
            <channel>
                <title>Test Feed</title>
                <link>http://example.com/</link>
                <description>Test feed description</description>
                <item>
                    <title>Item 1</title>
                    <link>http://example.com/item1</link>
                    <description>Item 1 description</description>
                </item>
            </channel>
        </rss>
    """,
    )

    # Serve the file using a simple HTTP server
    os.chdir(tmp_path)
    server = HTTPServer(("localhost", 0), SimpleHTTPRequestHandler)
    port: int = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url: str = f"http://localhost:{port}/test_feed.xml"

    feed: Feed = Feed.objects.create(url=url, domain="localhost")
    new_entries: int = fetch_and_archive_feed(feed)
    assert new_entries == 1

    # Check that the entry was archived and contains the expected data
    entry: Entry | None = Entry.objects.filter(feed=feed).first()
    assert entry is not None
    assert entry.data is not None
    assert entry.data["title"] == "Item 1"
    assert Entry.objects.filter(feed=feed).count() == 1

    # Clean up: stop the server and wait for the thread to finish
    server.shutdown()

    # Wait until the thread terminates.
    # This ensures the server is fully stopped before the test ends.
    thread.join()
