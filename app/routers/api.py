from __future__ import annotations

import datetime  # noqa: TCH003
from urllib.parse import unquote

from fastapi import APIRouter
from pydantic import BaseModel
from reader import ExceptionInfo, Feed, FeedNotFoundError

from app.dependencies import CommonReader  # noqa: TCH001
from app.validators import uri_validator

api_router = APIRouter(
    prefix="/api/v1",
    tags=["Feeds"],
    responses={404: {"description": "Not found"}},
)


class FeedOut(BaseModel):
    """The feed we return to the user."""

    url: str
    updated: datetime.datetime | None = None
    title: str | None = None
    link: str | None = None
    author: str | None = None
    subtitle: str | None = None
    version: str | None = None
    user_title: str | None = None
    added: datetime.datetime | None = None
    last_updated: datetime.datetime | None = None
    last_exception: ExceptionInfo | None = None
    updates_enabled: bool = True


@api_router.get("/feeds", summary="Get all the feeds in the reader.", tags=["Feeds"])
async def api_feeds(reader: CommonReader) -> list[Feed]:
    """Return all the feeds in the reader."""
    return list(reader.get_feeds())


@api_router.get(
    path="/feed/{feed_url:path}",
    summary="Get a feed from the reader.",
    tags=["Feeds"],
    response_model=FeedOut | dict[str, str],
    response_model_exclude_unset=True,
)
async def api_feed(feed_url: str, reader: CommonReader) -> Feed | dict[str, str]:
    """Return a feed from the reader."""
    feed_url = unquote(feed_url)

    if not uri_validator(feed_url):
        return {"message": "Invalid URL."}

    try:
        feed: Feed = reader.get_feed(feed_url)
    except FeedNotFoundError as e:
        return {"message": str(e)}
    return feed
