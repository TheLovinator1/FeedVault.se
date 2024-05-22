from __future__ import annotations

import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import click
from reader import Feed, ParseError, Reader, StorageError, UpdatedFeed, UpdateError, UpdateResult

from app.dependencies import get_reader

if TYPE_CHECKING:
    from collections.abc import Iterable


def add_broken_feed_to_csv(feed: Feed | UpdateResult | None) -> None:
    """Add a broken feed to a CSV file."""
    if feed is None:
        click.echo("Feed is None.", err=True)
        return

    with Path("broken_feeds.csv").open("a", encoding="utf-8") as f:
        f.write(f"{feed.url}\n")


@click.command()
def update_feeds() -> None:
    """Update all the feeds."""
    reader: Reader = get_reader()
    click.echo("Updating feeds...")

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

    click.echo(f"Feeds to update: {len(feeds)}")

    for feed in feeds:
        try:
            updated_feed: UpdatedFeed | None = reader.update_feed(feed)
            click.echo(f"Updated feed: {feed.url}")
            if updated_feed is not None:
                click.echo(
                    f"New: {updated_feed.new}, modified: {updated_feed.modified}, unmodified: {updated_feed.unmodified}",  # noqa: E501
                )

        except ParseError as e:
            # An error occurred while retrieving/parsing the feed.
            click.echo(f"Error parsing feed: {feed.url} ({e})", err=True)
        except UpdateError as e:
            # An error occurred while updating the feed.
            # Parent of all update-related exceptions.
            click.echo(f"Error updating feed: {feed.url} ({e})", err=True)
        except StorageError as e:
            # An exception was raised by the underlying storage.
            click.echo(f"Error updating feed: {feed.url}", err=True)
            click.echo(f"Storage error: {e}", err=True)
        except AssertionError:
            # An assertion failed.
            click.echo(f"Assertion error: {feed.url}", err=True)
            traceback.print_exc(file=sys.stderr)
            reader.disable_feed_updates(feed)
            add_broken_feed_to_csv(feed)

    click.echo("Feeds updated.")


if __name__ == "__main__":
    update_feeds()
