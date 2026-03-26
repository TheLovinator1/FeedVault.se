from typing import TYPE_CHECKING

from celery import shared_task

from feeds.models import Feed
from feeds.services import fetch_and_archive_feed

if TYPE_CHECKING:
    from celery import Task


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def archive_feed_task(self: Task, feed_id: int) -> str:
    """Celery task to fetch and archive a feed by its ID.

    Args:
        self: The task instance.
        feed_id: The ID of the Feed to archive.

    Returns:
        A message indicating the result of the archiving process.
    """
    try:
        feed: Feed = Feed.objects.get(id=feed_id)
    except Feed.DoesNotExist:
        return f"Feed with id {feed_id} does not exist."

    try:
        new_entries_count: int = fetch_and_archive_feed(feed)

    # TODO(TheLovinator): Replace with a specific exception type  # noqa: TD003
    except ValueError as e:
        raise self.retry(exc=e) from e
    else:
        if new_entries_count > 0:
            return f"Archived {new_entries_count} new entries for {feed.url}"
        return f"No new entries archived for {feed.url}"
