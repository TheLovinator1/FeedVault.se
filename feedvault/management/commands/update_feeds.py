from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from threading import Thread

from django.core.management.base import BaseCommand, no_translations
from django.db.models import Q
from django.utils import timezone
from rich.console import Console
from rich.progress import Progress

from feedvault.feeds import grab_entries
from feedvault.models import Feed

console = Console()


class DomainUpdater(Thread):
    def __init__(self, feeds: list[Feed], progress: Progress, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Update feeds in a separate thread.

        Args:
            feeds: The feeds to update.
            progress: The Rich progress bar.
            *args: Arbitrary positional arguments.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.feeds: list[Feed] = feeds
        self.progress: Progress = progress

    def run(self) -> None:
        with self.progress as progress:
            task = progress.add_task("[cyan]Updating feeds...", total=len(self.feeds))
            for feed in self.feeds:
                grab_entries(feed)
                progress.update(task, advance=1, description=f"[green]Updated {feed.feed_url}")


class Command(BaseCommand):
    help = "Check for new entries in feeds"
    requires_migrations_checks = True

    @no_translations
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        feeds = Feed.objects.filter(
            Q(last_checked__lte=timezone.now() - timedelta(minutes=15)) | Q(last_checked__isnull=True),
        )
        domain_feeds = defaultdict(list)

        for feed in feeds:
            domain_feeds[feed.domain.pk].append(feed)

        threads = []
        progress = Progress()

        for feeds in domain_feeds.values():
            thread = DomainUpdater(feeds, progress)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        console.log("[bold green]Successfully updated feeds")
