from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand

if TYPE_CHECKING:
    from reader import Reader


class Command(BaseCommand):
    help = "Update feeds"

    def handle(self, *args, **options) -> None:
        from feeds.get_reader import get_reader  # noqa: PLC0415

        reader: Reader = get_reader()
        reader.update_feeds()
