import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

from reader import (
    Feed,
    ParseError,
    Reader,
    StorageError,
    UpdatedFeed,
    UpdateError,
    UpdateResult,
)
from rich import print

from app.dependencies import get_reader
from cli.cli import app

if TYPE_CHECKING:
    from collections.abc import Iterable


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

    feeds: Iterable[Feed] = reader.get_feeds(
        broken=False,
        updates_enabled=True,
        new=True,
    )

    total_feeds: int | None = reader.get_feed_counts(
        broken=False,
        updates_enabled=True,
    ).total
    if not total_feeds:
        print("[bold red]No feeds to update[/bold red]")
        return

    print(f"Feeds to update: {total_feeds}")

    def update_feed(feed: Feed) -> None:
        try:
            updated_feed: UpdatedFeed | None = reader.update_feed(feed)
            if updated_feed is not None:
                print(
                    f"New: [green]{updated_feed.new}[/green], modified: [yellow]{updated_feed.modified}[/yellow], unmodified: {updated_feed.unmodified} - {feed.url}",  # noqa: E501
                )

        except ParseError as e:
            print(f"[bold red]Error parsing feed[/bold red]: {feed.url} ({e})")

        except UpdateError as e:
            print(f"[bold red]Error updating feed[/bold red]: {feed.url} ({e})")

        except StorageError as e:
            print(f"[bold red]Error updating feed[/bold red]: {feed.url}")
            print(f"[bold red]Storage error[/bold red]: {e}")

        except AssertionError:
            print(f"[bold red]Assertion error[/bold red]: {feed.url}")
            traceback.print_exc(file=sys.stderr)
            reader.disable_feed_updates(feed)
            _add_broken_feed_to_csv(feed)

        except KeyboardInterrupt:
            print("[bold red]Keyboard interrupt[/bold red]")
            reader.close()
            sys.exit(1)

    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(update_feed, feeds)

    print(f"Updated {total_feeds} feeds.")
