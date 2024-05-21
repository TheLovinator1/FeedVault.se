from __future__ import annotations

from typing import TYPE_CHECKING

import click
from reader import Reader, UpdateError

from app.dependencies import get_reader

if TYPE_CHECKING:
    from reader import UpdatedFeed


@click.command()
def update_feeds() -> None:
    """Update all the feeds."""
    click.echo("Updating feeds...")
    reader: Reader = get_reader()
    for feed in reader.update_feeds_iter():
        value: UpdatedFeed | None | UpdateError = feed.value
        if value is not None and isinstance(value, UpdateError):
            click.echo(f"Error updating {feed.url}: {value}")
        else:
            click.echo(f"Updated {feed.url}.")
    click.echo("Feeds updated.")


if __name__ == "__main__":
    update_feeds()
