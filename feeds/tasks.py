from celery import shared_task

from feeds.models import Feed
from feeds.services import fetch_and_archive_feed


@shared_task
def archive_feed_task(feed_id: int) -> str:
    """Celery task to fetch and archive a feed by its ID.

    Args:
        feed_id: The ID of the Feed to archive.

    Returns:
        A message indicating the result of the archiving process.
    """
    try:
        feed: Feed = Feed.objects.get(id=feed_id)
    except Feed.DoesNotExist:
        return f"Feed with id {feed_id} does not exist."
    new_entries_count: int = fetch_and_archive_feed(feed)
    if new_entries_count > 0:
        return f"Archived {new_entries_count} new entries for {feed.url}"
    return f"No new entries archived for {feed.url}"
