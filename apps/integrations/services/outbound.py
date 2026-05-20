"""SMS / WhatsApp orchestration stubs — swap with Celery tasks + provider adapters."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def schedule_delivery(notification_id: str) -> None:
    """
    Extend with Twilio/Africa's Talking/MessageBird implementations.
    The database row already persists the canonical record for audit readiness.
    """

    logger.debug("Outbound integrations placeholder for notification %s", notification_id)
