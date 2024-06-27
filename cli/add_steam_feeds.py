import sys
import traceback
from pathlib import Path

from reader import ParseError, Reader, StorageError, UpdateError
from rich import print

from app.dependencies import get_reader
from app.settings import DATA_DIR
from cli.cli import app


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
