from pathlib import Path

import requests
from rich import print

from app.settings import DATA_DIR
from cli.cli import app


@app.command(
    name="download_steam_ids",
    help="Download Steam IDs from the Steam API.",
)
def download_steam_ids() -> None:
    """Download Steam IDs from "https://api.steampowered.com/ISteamApps/GetAppList/v2/"."""
    print("Downloading Steam IDs...")

    r: requests.Response = requests.get(
        "https://api.steampowered.com/ISteamApps/GetAppList/v2/",
        timeout=10,
    )
    r.raise_for_status()

    data: dict[str, dict[str, list[dict[str, str]]]] = r.json()
    app_ids: list[dict[str, str]] = data["applist"]["apps"]

    file_path: Path = Path(DATA_DIR) / "steam_ids.txt"
    with file_path.open("w", encoding="utf-8") as f:
        for app_id in app_ids:
            f.write(f"{app_id["appid"]}\n")

    print(f"Steam IDs downloaded. {len(app_ids)} IDs saved to {file_path}.")
