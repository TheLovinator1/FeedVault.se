"""Admin interface for feeds app.

https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.contrib import admin

from feeds.models import (
    Author,
    Blocklist,
    Cloud,
    Contributor,
    Feed,
    Generator,
    Image,
    Info,
    Link,
    Publisher,
    Rights,
    Subtitle,
    Tags,
    TextInput,
    Title,
)
from feeds.validator import update_blocklist

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest

admin.site.register(Author)
admin.site.register(Cloud)
admin.site.register(Contributor)
admin.site.register(Feed)
admin.site.register(Generator)
admin.site.register(Image)
admin.site.register(Info)
admin.site.register(Link)
admin.site.register(Publisher)
admin.site.register(Rights)
admin.site.register(Subtitle)
admin.site.register(Tags)
admin.site.register(TextInput)
admin.site.register(Title)


# Add button to update blocklist on the admin page
@admin.register(Blocklist)
class BlocklistAdmin(admin.ModelAdmin):
    """Admin interface for blocklist."""

    actions: ClassVar[list[str]] = ["_update_blocklist", "delete_all_blocklist"]
    list_display: ClassVar[list[str]] = ["url", "active"]

    @admin.action(description="Update blocklist")
    def _update_blocklist(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:  # noqa: ARG002
        """Update blocklist."""
        msg: str = update_blocklist()
        self.message_user(request=request, message=msg)

    @admin.action(description="Delete all blocklists")
    def delete_all_blocklist(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:  # noqa: ARG002
        """Delete all blocklist from database."""
        Blocklist.objects.all().delete()
        self.message_user(request=request, message="Deleted all blocklists")
