from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from discord_webhook import DiscordWebhook
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

if TYPE_CHECKING:
    from requests import Response

logger: logging.Logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def notify_when_new_user(sender: User, instance: User, *, created: bool, **kwargs) -> None:  # noqa: ANN003, ARG001
    """Send a Discord notification when a new user is created.

    Args:
        sender: The User model.
        instance: The instance of the sender.
        created: A boolean indicating if the instance was created.
        **kwargs: Arbitrary keyword arguments.
    """
    if created:
        webhook_url: str | None = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            logger.error("Discord webhook URL not found.")
            return

        msg: str = f"New user registered on FeedVault 👀: {instance.username}"
        webhook = DiscordWebhook(url=webhook_url, content=msg)
        response: Response = webhook.execute()
        logger.info("Discord notification sent: (%s) %s", response.status_code, response.text)
