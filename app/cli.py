from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click
from reader import Feed, Reader, UpdateError, UpdateResult
from reader.types import UpdatedFeed

from app.dependencies import get_reader

if TYPE_CHECKING:
    from reader import UpdatedFeed


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

    for feed in reader.update_feeds_iter(updates_enabled=True, workers=100):
        url: str = feed.url
        value: UpdatedFeed | None | UpdateError = feed.value

        if isinstance(value, UpdateError):
            add_broken_feed_to_csv(feed)
            reader.disable_feed_updates(url)
            continue

        if value is None:
            click.echo(f"Feed not updated: {url}")
            continue

        click.echo(f"Updated feed: {url}")

    click.echo("Feeds updated.")


if __name__ == "__main__":
    reader: Reader = get_reader()

    for feed in reader.get_feeds(updates_enabled=False):
        reader.enable_feed_updates(feed)

    update_feeds()
