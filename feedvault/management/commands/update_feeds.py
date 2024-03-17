from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand, no_translations
from django.db.models import Q
from django.utils import timezone

from feedvault.feeds import grab_entries
from feedvault.models import Entry, Feed


class Command(BaseCommand):
    help = "Check for new entries in feeds"
    requires_migrations_checks = True

    @no_translations
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        new_entries: int = 0

        # Grab feeds that haven't been checked in 15 minutes OR haven't been checked at all
        for feed in Feed.objects.filter(
            Q(last_checked__lte=timezone.now() - timedelta(minutes=15)) | Q(last_checked__isnull=True),
        ):
            entries: None | list[Entry] = grab_entries(feed)
            if not entries:
                self.stdout.write(f"No new entries for {feed.title}")
                continue

            self.stdout.write(f"Updated {feed}")
            self.stdout.write(f"Added {len(entries)} new entries for {feed}")
            new_entries += len(entries)

        if new_entries:
            self.stdout.write(self.style.SUCCESS(f"Successfully updated feeds. Added {new_entries} new entries"))

        self.stdout.write("No new entries found")
