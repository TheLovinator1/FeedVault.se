"""These models are used to store the data from https://reader.readthedocs.io/en/latest/api.html#reader.Feed."""

from __future__ import annotations

import typing
import uuid
from pathlib import Path

from django.db import models


def get_upload_path(instance: UploadedFeed, filename: str) -> str:
    """Don't save the file with the original filename."""
    ext: str = Path(filename).suffix
    unix_time: int = int(instance.created_at.timestamp())
    filename = f"{unix_time}-{uuid.uuid4().hex}{ext}"
    return f"uploads/{filename}"


class UploadedFeed(models.Model):
    """A file uploaded to the server by a user."""

    file = models.FileField(upload_to=get_upload_path, help_text="The file that was uploaded.")
    original_filename = models.TextField(help_text="The original filename of the file.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The time the file was uploaded.")
    has_been_processed = models.BooleanField(default=False, help_text="Has the file content been added to the archive?")
    public = models.BooleanField(default=False, help_text="Is the file public?")
    description = models.TextField(blank=True, help_text="Description added by user.")
    notes = models.TextField(blank=True, help_text="Notes from admin.")

    class Meta:
        """Meta information for the uploaded file model."""

        ordering: typing.ClassVar[list[str]] = ["-created_at"]
        verbose_name: str = "Uploaded file"
        verbose_name_plural: str = "Uploaded files"

    def __str__(self: UploadedFeed) -> str:
        return f"{self.original_filename} - {self.created_at}"


class Feed(models.Model):
    url = models.URLField(unique=True, help_text="The URL of the feed.")
    updated = models.DateTimeField(help_text="The date the feed was last updated, according to the feed.", null=True)
    title = models.TextField(help_text="The title of the feed.", null=True)
    link = models.TextField(help_text="The URL of a page associated with the feed.", null=True)
    author = models.TextField(help_text="The author of the feed.", null=True)
    subtitle = models.TextField(help_text="A description or subtitle for the feed.", null=True)
    version = models.TextField(help_text="The version of the feed.", null=True)
    user_title = models.TextField(help_text="User-defined feed title.", null=True)
    added = models.DateTimeField(help_text="The date when the feed was added.", auto_now_add=True)
    last_updated = models.DateTimeField(help_text="The date when the feed was last retrieved by reader.", null=True)
    last_exception_type_name = models.TextField(help_text="The fully qualified name of the exception type.", null=True)
    last_exception_value = models.TextField(help_text="The exception value.", null=True)
    last_exception_traceback = models.TextField(help_text="The exception traceback.", null=True)
    updates_enabled = models.BooleanField(help_text="Whether updates are enabled for the feed.", default=True)
    stale = models.BooleanField(
        help_text="Whether the next update should update all entries, regardless of their hash or updated.",
        default=False,
    )
    http_etag = models.TextField(help_text="The HTTP ETag header.", null=True)
    http_last_modified = models.TextField(help_text="The HTTP Last-Modified header.", null=True)
    data_hash = models.BinaryField(help_text="The hash of the feed data.", null=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.url})" if self.title else self.url


class Entry(models.Model):
    feed = models.ForeignKey(
        Feed, on_delete=models.CASCADE, help_text="The feed this entry is from.", related_name="entries"
    )
    id = models.TextField(primary_key=True, help_text="The entry id.")
    updated = models.DateTimeField(help_text="The date the entry was last updated, according to the feed.", null=True)
    title = models.TextField(help_text="The title of the entry.", null=True)
    link = models.TextField(help_text="The URL of the entry.", null=True)
    author = models.TextField(help_text="The author of the feed.", null=True)
    published = models.DateTimeField(help_text="The date the entry was published.", null=True)
    summary = models.TextField(help_text="A summary of the entry.", null=True)
    read = models.BooleanField(help_text="Whether the entry has been read.", default=False)
    read_modified = models.DateTimeField(help_text="When read was last modified, None if that never.", null=True)
    added = models.DateTimeField(help_text="The date when the entry was added (first updated) to reader.", null=True)
    added_by = models.TextField(help_text="The source of the entry. One of 'feed', 'user'.", null=True)
    last_updated = models.DateTimeField(help_text="The date when the entry was last retrieved by reader.", null=True)
    first_updated = models.DateTimeField(help_text="The date when the entry was first retrieved by reader.", null=True)
    first_updated_epoch = models.DateTimeField(
        help_text="The date when the entry was first retrieved by reader, as an epoch timestamp.", null=True
    )
    feed_order = models.PositiveIntegerField(help_text="The order of the entry in the feed.", null=True)
    recent_sort = models.PositiveIntegerField(help_text="The order of the entry in the recent list.", null=True)
    sequence = models.BinaryField(help_text="The sequence of the entry in the feed.", null=True)
    original_feed = models.TextField(
        help_text="The URL of the original feed of the entry. If the feed URL never changed, the same as feed_url.",
        null=True,
    )
    data_hash = models.TextField(help_text="The hash of the entry data.", null=True)
    data_hash_changed = models.BooleanField(
        help_text="Whether the data hash has changed since the last update.", default=False
    )
    important = models.BooleanField(help_text="Whether the entry is important.", default=False)
    important_modified = models.DateTimeField(
        help_text="When important was last modified, None if that never.", null=True
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.link})" if self.title and self.link else self.id


class Content(models.Model):
    entry = models.ForeignKey(
        Entry, on_delete=models.CASCADE, help_text="The entry this content is for.", related_name="content"
    )
    value = models.TextField(help_text="The content value.")
    type = models.TextField(help_text="The content type.", null=True)
    language = models.TextField(help_text="The content language.", null=True)

    def __str__(self) -> str:
        max_length = 50
        return self.value[:max_length] + "..." if len(self.value) > max_length else self.value


class Enclosure(models.Model):
    entry = models.ForeignKey(
        Entry, on_delete=models.CASCADE, help_text="The entry this enclosure is for.", related_name="enclosures"
    )
    href = models.TextField(help_text="The file URL.")
    type = models.TextField(help_text="The file content type.", null=True)
    length = models.PositiveIntegerField(help_text="The file length.", null=True)

    def __str__(self) -> str:
        return self.href
