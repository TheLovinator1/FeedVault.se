from __future__ import annotations

import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

import requests
import typer
from reader import Feed, ParseError, Reader, StorageError, UpdatedFeed, UpdateError, UpdateResult
from rich import print

from app.dependencies import get_reader
from app.scrapers.rss_link_database import scrape
from app.settings import DATA_DIR

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

    feeds: Iterable[Feed] = reader.get_feeds(broken=False, updates_enabled=True, new=True)

    total_feeds: int | None = reader.get_feed_counts(broken=False, updates_enabled=True).total
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


@app.command(
    name="download_steam_ids",
    help="Download Steam IDs from the Steam API.",
)
def download_steam_ids() -> None:
    """Download Steam IDs from "https://api.steampowered.com/ISteamApps/GetAppList/v2/"."""
    print("Downloading Steam IDs...")

    r: requests.Response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/", timeout=10)
    r.raise_for_status()

    data: dict[str, dict[str, list[dict[str, str]]]] = r.json()
    app_ids: list[dict[str, str]] = data["applist"]["apps"]

    file_path: Path = Path(DATA_DIR) / "steam_ids.txt"
    with file_path.open("w", encoding="utf-8") as f:
        for app_id in app_ids:
            f.write(f"{app_id["appid"]}\n")

    print(f"Steam IDs downloaded. {len(app_ids)} IDs saved to {file_path}.")


@app.command(
    name="add_steam_feeds",
    help="Add Steam feeds to the reader. Needs 'download_steam_ids' to be run first.",
)
def add_steam_feeds() -> None:
    """Add the ids from "steam_ids.txt" to the reader."""
    reader: Reader = get_reader()
    print("Adding Steam feeds...")

    file_path: Path = Path(DATA_DIR) / "steam_ids.txt"
    if not file_path.exists():
        print("File not found.")
        return

    with file_path.open("r", encoding="utf-8") as f:
        steam_ids: list[str] = f.read().splitlines()

    for count, steam_id in enumerate(steam_ids):
        try:
            reader.add_feed(f"https://store.steampowered.com/feeds/news/app/{steam_id}")
            print(f"[{count}/{len(steam_ids)}] Added feed: {steam_id}")

        except ParseError as e:
            print(f"[bold red]Error parsing feed[/bold red] ({e})")

        except UpdateError as e:
            print(f"[bold red]Error updating feed[/bold red] ({e})")

        except StorageError as e:
            print(f"[bold red]Error updating feed[/bold red] ({e})")

        except AssertionError as e:
            print(f"[bold red]Assertion error[/bold red] ({e})")
            traceback.print_exc(file=sys.stderr)

        except KeyboardInterrupt:
            print("[bold red]Keyboard interrupt[/bold red]")
            reader.close()
            sys.exit(1)

    print(f"Added {len(steam_ids)} Steam feeds.")


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
