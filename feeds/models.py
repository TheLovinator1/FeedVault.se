from __future__ import annotations

from typing import Literal

from django.db import models
from django.db.models import JSONField


class Domain(models.Model):
    """A domain that has one or more feeds."""

    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    categories = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(default=False)
    hidden_at = models.DateTimeField(null=True, blank=True)
    hidden_reason = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return string representation of the domain."""
        if_hidden: Literal[" (hidden)", ""] = " (hidden)" if self.hidden else ""
        return self.name + if_hidden


class Feed(models.Model):
    """A RSS/Atom/JSON feed."""

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # General data
    bozo = models.BooleanField()
    bozo_exception = models.TextField()
    encoding = models.TextField()
    etag = models.TextField()
    headers = JSONField()
    href = models.TextField()
    modified = models.DateTimeField()
    namespaces = JSONField()
    status = models.IntegerField()
    version = models.CharField(max_length=50)
    # Feed data
    author = models.TextField()
    author_detail = JSONField()
    cloud = JSONField()
    contributors = JSONField()
    docs = models.TextField()
    errorreportsto = models.TextField()
    generator = models.TextField()
    generator_detail = models.TextField()
    icon = models.TextField()
    _id = models.TextField()
    image = JSONField()
    info = models.TextField()
    info_detail = JSONField()
    language = models.TextField()
    license = models.TextField()
    link = models.TextField()
    links = JSONField()
    logo = models.TextField()
    published = models.TextField()
    published_parsed = models.DateTimeField()
    publisher = models.TextField()
    publisher_detail = JSONField()
    rights = models.TextField()
    rights_detail = JSONField()
    subtitle = models.TextField()
    subtitle_detail = JSONField()
    tags = JSONField()
    textinput = JSONField()
    title = models.TextField()
    title_detail = JSONField()
    ttl = models.TextField()
    updated = models.TextField()
    updated_parsed = models.DateTimeField()

    def __str__(self) -> str:
        """Return string representation of the feed."""
        return self.title_detail["value"] or "No title"


class Entry(models.Model):
    """Each feed has multiple entries."""

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Entry data
    author = models.TextField()
    author_detail = JSONField()
    comments = models.TextField()
    content = JSONField()
    contributors = JSONField()
    created = models.TextField()
    created_parsed = models.DateTimeField()
    enclosures = JSONField()
    expired = models.TextField()
    expired_parsed = models.DateTimeField()
    _id = models.TextField()
    license = models.TextField()
    link = models.TextField()
    links = JSONField()
    published = models.TextField()
    published_parsed = models.DateTimeField()
    publisher = models.TextField()
    publisher_detail = JSONField()
    source = JSONField()
    summary = models.TextField()
    summary_detail = JSONField()
    tags = JSONField()
    title = models.TextField()
    title_detail = JSONField()
    updated = models.TextField()
    updated_parsed = models.DateTimeField()

    def __str__(self) -> str:
        """Return string representation of the entry."""
        return self.title_detail["value"] or "No title"
