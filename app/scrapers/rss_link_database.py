"""Scrape https://github.com/rumca-js/RSS-Link-Database for RSS links."""

from pathlib import Path

import orjson
from click import echo


def scrape() -> str:
    """Scrape.

    Raises:
        FileNotFoundError: If the RSS-Link-Database repository is not found.
    """
    repository_path = Path("RSS-Link-Database")
    if not repository_path.exists():
        msg = "RSS-Link-Database repository not found."
        raise FileNotFoundError(msg)

    rss_links: list[str] = []
    for file in repository_path.glob("*.json"):
        echo(f"Scraping {file.name}...")

        with file.open("r", encoding="utf-8") as f:
            data = orjson.loads(f.read())

            for d in data:
                if d.get("url"):
                    rss_links.append(d["url"])

                if d.get("link"):
                    rss_links.append(d["link"])

    rss_links = list(set(rss_links))
    return "\n".join(rss_links)
