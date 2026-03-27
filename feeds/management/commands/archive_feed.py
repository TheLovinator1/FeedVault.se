from typing import TYPE_CHECKING
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models.query import QuerySet

from feeds.models import Entry
from feeds.models import Feed
from feeds.services import fetch_and_archive_feed

if TYPE_CHECKING:
    from django.core.management.base import CommandParser
    from pytest_django.asserts import QuerySet


class Command(BaseCommand):
    """Django management command to fetch and archive a feed by URL."""

    help = "Fetch and archive a feed by URL."
    amount_to_show: int = 10

    def add_arguments(self, parser: CommandParser) -> None:
        """Add URL argument and options to the command."""
        parser.add_argument(
            "url",
            type=str,
            help="Feed URL to fetch and archive.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove all entries for this feed before archiving.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run the command non-interactively, skipping confirmations.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        """Handle the command execution."""
        url: str = options["url"]
        reset: bool = options.get("reset", False)
        force: bool = options.get("force", False)

        feed, created = Feed.objects.get_or_create(url=url)

        if created:
            msg = f"Created new feed for URL: {url}"
            self.stdout.write(self.style.SUCCESS(msg))

        if reset:
            entries_qs: QuerySet[Entry, Entry] = Entry.objects.filter(feed=feed)
            count: int = entries_qs.count()

            if count == 0:
                msg = f"No entries found for feed: {url}"
                self.stdout.write(self.style.WARNING(msg))
            else:
                proceed: bool = True
                if not force:
                    proceed: bool = self.confirm_and_list_entries(
                        url=url,
                        entries_qs=entries_qs,
                        count=count,
                    )
                if proceed:
                    entries_qs.delete()
                    msg = f"Deleted {count} entries for feed: {url}"
                    self.stdout.write(self.style.SUCCESS(msg))

        new_entries: int = fetch_and_archive_feed(feed)
        if new_entries:
            msg: str = f"Archived {new_entries} new entr{'y' if new_entries == 1 else 'ies'} for URL: {url}"
            self.stdout.write(self.style.SUCCESS(msg))

        else:
            msg: str = "\tFeed is up to date, but no new entries were archived."
            self.stdout.write(self.style.WARNING(msg))

    def confirm_and_list_entries(
        self,
        url: str,
        entries_qs: QuerySet[Entry, Entry],
        count: int,
    ) -> bool:
        """Confirm with the user before deleting entries and list some of them.

        Args:
            url (str): The URL of the feed.
            entries_qs (QuerySet[Entry, Entry]): The queryset of entries to be deleted.
            count (int): The total number of entries to be deleted.

        Returns:
            True if user confirms, False otherwise.
        """
        msg: str = f"The following {count} entries will be removed for feed: {url}"
        self.stdout.write(self.style.WARNING(msg))

        entries: QuerySet[Entry, Entry] = entries_qs.order_by("-published_at")
        entries = entries[: self.amount_to_show]
        for entry in entries:
            title: str | None = get_entry_title(entry)
            self.stdout.write(f"- {title}")

        confirm: str = input("Are you sure you want to proceed? (yes/no): ")
        if confirm.lower() != "yes":
            self.stdout.write(self.style.ERROR("Operation cancelled."))
            return False
        return True


def get_entry_title(entry: Entry) -> str | None:
    """Get the title from an entry's data.

    Args:
        entry (Entry): The Entry object from which to extract the title.

    Returns:
        str | None: The title of the entry if available, otherwise None.
    """
    # entry_data is a JSONField
    entry_data: dict[str, Any] | list[Any] | None = entry.data

    if not isinstance(entry_data, dict):
        return None

    return entry_data.get("title")
