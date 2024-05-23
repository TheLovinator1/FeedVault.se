from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from reader import FeedExistsError, InvalidFeedURLError

from app.dependencies import CommonReader, CommonStats  # noqa: TCH001
from app.settings import MEDIA_ROOT

if TYPE_CHECKING:
    from collections.abc import Iterable

    from fastapi.datastructures import Address
    from reader import Feed


logger: logging.Logger = logging.getLogger(__name__)

static_router = APIRouter(tags=["HTML"])
templates = Jinja2Templates(directory="templates")


@static_router.get("/favicon.ico", summary="Favicon.", tags=["HTML"])
async def favicon(request: Request):
    """Favicon."""
    return FileResponse("static/favicon.ico")


@static_router.get(path="/", summary="Index page.", tags=["HTML"])
async def index(request: Request, reader: CommonReader, stats: CommonStats):
    """Index page."""
    feeds: Iterable[Feed] = reader.get_feeds(limit=15)
    return templates.TemplateResponse(request=request, name="index.html", context={"feeds": feeds, "stats": stats})


@static_router.get(path="/feeds", summary="Feeds page.", tags=["HTML"])
async def feeds(
    request: Request,
    reader: CommonReader,
    stats: CommonStats,
    next_url: str | None = None,
    prev_url: str | None = None,
):
    """Feeds page."""
    if next_url:
        feeds = list(reader.get_feeds(starting_after=next_url, limit=15))
    elif prev_url:
        feeds = list(reader.get_feeds(starting_after=prev_url, limit=15))
    else:
        feeds = list(reader.get_feeds(limit=15))

    # This is the last feed on the page.
    next_url = feeds[-1].url if feeds else None

    # This is the first feed on the page.
    prev_url = feeds[0].url if feeds else None

    return templates.TemplateResponse(
        request=request,
        name="feeds.html",
        context={"feeds": feeds, "stats": stats, "next_url": next_url, "prev_url": prev_url},
    )


@static_router.get(path="/feed/{feed_url:path}", summary="Feed page.", tags=["HTML"])
async def feed(request: Request, feed_url: str, reader: CommonReader, stats: CommonStats):
    """Feed page."""
    feed: Feed = reader.get_feed(feed_url)
    entries = list(reader.get_entries(feed=feed.url))
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"feed": feed, "entries": entries, "stats": stats},
    )


@static_router.get(path="/search", summary="Search page.", tags=["HTML"])
async def search(  # noqa: PLR0913, PLR0917
    request: Request,
    q: str,
    reader: CommonReader,
    stats: CommonStats,
    next_feed: str | None = None,
    next_entry: str | None = None,
    prev_feed: str | None = None,
    prev_entry: str | None = None,
):
    """Search page."""
    if next_feed and next_entry:
        entries = list(reader.search_entries(q, starting_after=(next_feed, next_entry), limit=15))
    elif prev_feed and prev_entry:
        entries = list(reader.search_entries(q, starting_after=(prev_feed, prev_entry), limit=15))
    else:
        entries = list(reader.search_entries(q, limit=15))

    # TODO(TheLovinator): We need to show the entries in the search results.  # noqa: TD003
    reader.update_search()

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "query": q,
            "entries": entries,
            "stats": stats,
            "next_feed": next_feed,
            "next_entry": next_entry,
            "prev_feed": prev_feed,
            "prev_entry": prev_entry,
        },
    )


@static_router.post(path="/upload", summary="Upload files.", tags=["HTML"])
async def upload_files(request: Request, files: list[UploadFile] = File(...)):
    """Upload files."""
    media_root: str = os.getenv(key="MEDIA_ROOT", default=MEDIA_ROOT.as_posix())
    file_infos: list[dict[str, str]] = []
    upload_time = int(time.time())

    # Save metadata
    request_client: Address | None = request.client
    if request_client:
        host: str = request_client.host or "unknown"
    else:
        host = "unknown"

    metadata = {
        "upload_time": upload_time,
        "files": [file.filename for file in files if file.filename],
        "ip": host,
        "user_agent": request.headers.get("user-agent") or "unknown",
        "description": request.headers.get("description") or "No description.",
    }
    metadata_path: Path = Path(media_root) / f"{upload_time}.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(str(metadata))

    # Save uploaded files
    for file in files:
        if not file:
            logger.error("No file uploaded.")
            continue

        if not file.filename:
            logger.error("No file name.")
            continue

        file_path: Path = Path(media_root) / f"{upload_time}" / file.filename

        content: bytes = b""
        while chunk := await file.read(1024):  # Read in chunks of 1024 bytes
            content += chunk

        file_path.parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_bytes(content)

        file_infos.append({"filename": file.filename})

    return {"files_uploaded": file_infos}


@static_router.get(path="/upload", summary="Upload page.", tags=["HTML"])
async def upload_page(request: Request, stats: CommonStats):
    """Upload page."""
    return templates.TemplateResponse(request=request, name="upload.html", context={"stats": stats})


@static_router.get(path="/contact", summary="Contact page.", tags=["HTML"])
async def contact(request: Request, stats: CommonStats):
    """Contact page."""
    return templates.TemplateResponse(request=request, name="contact.html", context={"stats": stats})


@static_router.post(path="/contact", summary="Contact page.", tags=["HTML"])
async def contact_form(request: Request, stats: CommonStats, message: str = Form(...)):
    """Contact page."""
    # TODO(TheLovinator): Send the message to the admin.  # noqa: TD003
    return {
        "message": message,
        "stats": stats,
    }


@static_router.get(path="/add", summary="Add feeds page.", tags=["HTML"])
async def add_page(request: Request, stats: CommonStats):
    """Add feeds page."""
    return templates.TemplateResponse(request=request, name="add.html", context={"stats": stats})


@static_router.post(path="/add", summary="Add feeds page.", tags=["HTML"])
async def add_feed(reader: CommonReader, stats: CommonStats, feed_urls: str = Form(...)):
    """Add feeds page."""
    feed_info: list[dict[str, str]] = []
    # Each line is a feed URL.
    for feed_url in feed_urls.split("\n"):
        try:
            reader.add_feed(feed_url.strip())
            feed_info.append({"url": feed_url.strip(), "status": "Added"})
        except FeedExistsError as e:
            feed_info.append({"url": feed_url.strip(), "status": str(e)})
        except InvalidFeedURLError as e:
            feed_info.append({"url": feed_url.strip(), "status": str(e)})

    return {
        "feed_urls": feed_urls,
        "stats": stats,
        "feed_info": feed_info,
    }
