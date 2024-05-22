from __future__ import annotations

import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from reader import Feed, ParseError, Reader, StorageError, UpdatedFeed, UpdateError, UpdateResult
from rich import print

from app.dependencies import get_reader
from app.scrapers.rss_link_database import scrape

if TYPE_CHECKING:
    from collections.abc import Iterable

app = typer.Typer(
    name="FeedVault CLI",
    no_args_is_help=True,
)


def _add_broken_feed_to_csv(feed: Feed | UpdateResult | None) -> None:
    """Add a broken feed to a CSV file."""
    if feed is None:
        print("Feed is None.")
        return

    with Path("broken_feeds.csv").open("a", encoding="utf-8") as f:
        f.write(f"{feed.url}\n")


@app.command(
    name="update_feeds",
    help="Update all the feeds.",
)
def update_feeds() -> None:
    """Update all the feeds."""
    reader: Reader = get_reader()
    print("Updating feeds...")

    all_feeds: Iterable[Feed] = reader.get_feeds(updates_enabled=True, broken=False)
    feeds: list[Feed] = []

    # Only get feeds that hasn't been updated in the last 3 hours
    for feed in all_feeds:
        if feed.last_updated:
            now: datetime = datetime.now(tz=feed.last_updated.tzinfo)
            delta: timedelta = now - feed.last_updated

            three_hours: int = 60 * 60 * 3
            if delta.total_seconds() < three_hours:
                feeds.append(feed)
        else:
            feeds.append(feed)

    print(f"Feeds to update: {len(feeds)}")

    for feed in feeds:
        try:
            updated_feed: UpdatedFeed | None = reader.update_feed(feed)
            print(f"Updated feed: {feed.url}")
            if updated_feed is not None:
                print(
                    f"New: [green]{updated_feed.new}[/green], modified: [yellow]{updated_feed.modified}[/yellow], unmodified: {updated_feed.unmodified}",  # noqa: E501
                )

        except ParseError as e:
            # An error occurred while retrieving/parsing the feed.
            print(f"[bold red]Error parsing feed[/bold red]: {feed.url} ({e})")
        except UpdateError as e:
            # An error occurred while updating the feed.
            # Parent of all update-related exceptions.
            print(f"[bold red]Error updating feed[/bold red]: {feed.url} ({e})")
        except StorageError as e:
            # An exception was raised by the underlying storage.
            print(f"[bold red]Error updating feed[/bold red]: {feed.url}")
            print(f"[bold red]Storage error[/bold red]: {e}")
        except AssertionError:
            # An assertion failed.
            print(f"[bold red]Assertion error[/bold red]: {feed.url}")
            traceback.print_exc(file=sys.stderr)
            reader.disable_feed_updates(feed)
            _add_broken_feed_to_csv(feed)

    print("Feeds updated.")


@app.command(
    name="grab_links",
    help="Grab RSS feeds from different sources.",
)
def grab_links() -> None:
    """Grab RSS feeds from different sources."""
    print("Grabbing links...")
    rss_links: str = scrape()
    print(rss_links)


if __name__ == "__main__":
    app()
