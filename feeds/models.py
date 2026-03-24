import logging
from urllib.parse import urlparse

from django.contrib.postgres.indexes import GinIndex
from django.db import models

logger: logging.Logger = logging.getLogger("feeds.models")


class Feed(models.Model):
    """Represents the actual RSS/Atom feed URL and its metadata."""

    url = models.URLField(
        help_text="The canonical URL of the RSS/Atom feed. Must be unique.",
        verbose_name="Feed URL",
        max_length=2048,
        unique=True,
    )
    domain = models.CharField(
        help_text="Domain name extracted from the feed URL.",
        verbose_name="Domain",
        max_length=255,
        db_index=True,
    )
    etag = models.CharField(
        help_text="HTTP ETag header for conditional requests.",
        verbose_name="ETag",
        max_length=255,
        blank=True,
        default="",
    )
    last_modified = models.CharField(
        help_text="HTTP Last-Modified header for conditional requests.",
        verbose_name="Last Modified",
        max_length=255,
        blank=True,
        default="",
    )
    is_active = models.BooleanField(
        help_text="Whether this feed is currently being fetched.",
        verbose_name="Is Active",
        default=True,
    )
    created_at = models.DateTimeField(
        help_text="Timestamp when this feed was first added.",
        verbose_name="Created At",
        auto_now_add=True,
    )
    last_fetched_at = models.DateTimeField(
        help_text="Timestamp when this feed was last fetched.",
        verbose_name="Last Fetched At",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Feed"
        verbose_name_plural = "Feeds"

    def __str__(self) -> str:
        """Return the feed URL as string representation."""
        return self.url

    def save(self, *args, **kwargs) -> None:
        """Override save to auto-populate domain from URL if not set."""
        if not self.domain and self.url:
            self.domain = str(urlparse(str(self.url)).netloc)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "Auto-populated domain '%s' for feed URL: %s",
                    self.domain,
                    self.url,
                )

        super().save(*args, **kwargs)


class Entry(models.Model):
    """An archived entry (item/post) from a feed."""

    feed = models.ForeignKey(
        to="Feed",
        help_text="The feed this entry was fetched from.",
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="Feed",
    )
    entry_id = models.CharField(
        help_text="Unique entry ID (guid, id, or link) from the feed.",
        verbose_name="Entry ID",
        max_length=512,
        db_index=True,
    )
    fetched_at = models.DateTimeField(
        help_text="Timestamp when this entry was archived.",
        verbose_name="Fetched At",
        auto_now_add=True,
        db_index=True,
    )
    published_at = models.DateTimeField(
        help_text="Timestamp when this entry was published (if available).",
        verbose_name="Published At",
        db_index=True,
        blank=True,
        null=True,
    )
    content_hash = models.BigIntegerField(
        help_text="xxhash64 integer of the entry content for deduplication.",
        verbose_name="Content Hash",
        db_index=True,
    )
    data = models.JSONField(
        help_text="Parsed entry data as JSON.",
        verbose_name="Entry Data",
        blank=True,
        null=True,
    )
    error_message = models.TextField(
        help_text="Error message if archiving failed.",
        verbose_name="Error Message",
        blank=True,
        default="",
    )

    class Meta:
        unique_together = ("feed", "entry_id", "content_hash")
        indexes = [
            GinIndex(fields=["data"]),
        ]
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __str__(self) -> str:
        """Return a string representation of the entry."""
        return f"{self.feed.domain} entry {self.entry_id} at {self.fetched_at}"
