from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand

from feeds.models import Feed
from feeds.services import fetch_and_archive_feed

if TYPE_CHECKING:
    from django.core.management.base import CommandParser


class Command(BaseCommand):
    """Django management command to fetch and archive a feed by URL."""

    help = "Fetch and archive a feed by URL."

    def add_arguments(self, parser: CommandParser) -> None:
        """Add URL argument to the command."""
        parser.add_argument("url", type=str, help="Feed URL to fetch and archive.")

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        """Handle the command execution."""
        url: str = options["url"]
        feed, created = Feed.objects.get_or_create(url=url)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new feed for URL: {url}"))

        new_entries: int = fetch_and_archive_feed(feed)
        if new_entries:
            msg: str = f"Archived {new_entries} new entr{'y' if new_entries == 1 else 'ies'} for URL: {url}"
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            msg: str = "\tFeed is up to date, but no new entries were archived."
            self.stdout.write(self.style.WARNING(msg))
