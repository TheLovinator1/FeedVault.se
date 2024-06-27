from rich import print

from app.scrapers.rss_link_database import scrape
from cli.cli import app


@app.command(
    name="grab_links",
    help="Grab RSS feeds from different sources.",
)
def grab_links() -> None:
    """Grab RSS feeds from different sources."""
    print("Grabbing links...")
    rss_links: str = scrape()
    print(rss_links)
