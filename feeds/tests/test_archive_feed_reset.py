import builtins
from typing import TYPE_CHECKING

import pytest
from django.core.management import call_command

from feeds.models import Entry
from feeds.models import Feed

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.django_db
def test_reset_option_removes_only_feed_entries(db: None) -> None:
    """Test that the --reset option in the archive_feed command only removes entries for the specified feed."""
    url1 = "http://example.com/feed1.xml"
    url2 = "http://example.com/feed2.xml"
    feed1: Feed = Feed.objects.create(url=url1, domain="example.com")
    feed2: Feed = Feed.objects.create(url=url2, domain="example.com")

    # Create entries for both feeds
    _e1: Entry = Entry.objects.create(feed=feed1, entry_id="a", content_hash=1)
    _e2: Entry = Entry.objects.create(feed=feed1, entry_id="b", content_hash=2)
    _e3: Entry = Entry.objects.create(feed=feed2, entry_id="c", content_hash=3)
    assert Entry.objects.filter(feed=feed1).count() == 2
    assert Entry.objects.filter(feed=feed2).count() == 1

    # Simulate user confirmation by patching input
    orig_input: Callable[[object], str] = builtins.input
    builtins.input = lambda _: "yes"
    try:
        call_command("archive_feed", url1, "--reset")
    finally:
        builtins.input = orig_input

    # Only feed1's entries should be deleted
    assert Entry.objects.filter(feed=feed1).count() == 0
    assert Entry.objects.filter(feed=feed2).count() == 1
