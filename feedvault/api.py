from __future__ import annotations

from django.http import HttpRequest  # noqa: TCH002
from ninja import ModelSchema, NinjaAPI
from ninja.pagination import paginate

from feedvault.models import Domain, Entry, Feed

api_v1 = NinjaAPI(
    title="FeedVault API",
    version="0.1.0",
    description="FeedVault API",
    urls_namespace="api_v1",
)


class FeedOut(ModelSchema):
    class Meta:
        model = Feed
        fields: str = "__all__"


class EntriesOut(ModelSchema):
    class Meta:
        model = Entry
        fields: str = "__all__"


class DomainsOut(ModelSchema):
    class Meta:
        model = Domain
        fields: str = "__all__"


@api_v1.get("/feeds/", response=list[FeedOut])
@paginate
def list_feeds(request: HttpRequest) -> None:
    """Get a list of feeds."""
    return Feed.objects.all()  # type: ignore  # noqa: PGH003


@api_v1.get("/feeds/{feed_id}/", response=FeedOut)
def get_feed(request: HttpRequest, feed_id: int) -> Feed:
    """Get a feed by ID."""
    return Feed.objects.get(id=feed_id)


@api_v1.get("/feeds/{feed_id}/entries/", response=list[EntriesOut])
@paginate
def list_entries(request: HttpRequest, feed_id: int) -> list[Entry]:
    """Get a list of entries for a feed."""
    return Entry.objects.filter(feed_id=feed_id)  # type: ignore  # noqa: PGH003


@api_v1.get("/entries/", response=list[EntriesOut])
@paginate
def list_all_entries(request: HttpRequest) -> list[Entry]:
    """Get a list of entries."""
    return Entry.objects.all()  # type: ignore  # noqa: PGH003


@api_v1.get("/entries/{entry_id}/", response=EntriesOut)
def get_entry(request: HttpRequest, entry_id: int) -> Entry:
    """Get an entry by ID."""
    return Entry.objects.get(id=entry_id)


@api_v1.get("/domains/", response=list[DomainsOut])
@paginate
def list_domains(request: HttpRequest) -> list[Domain]:
    """Get a list of domains."""
    return Domain.objects.all()  # type: ignore  # noqa: PGH003


@api_v1.get("/domains/{domain_id}/", response=DomainsOut)
def get_domain(request: HttpRequest, domain_id: int) -> Domain:
    """Get a domain by ID."""
    return Domain.objects.get(id=domain_id)
