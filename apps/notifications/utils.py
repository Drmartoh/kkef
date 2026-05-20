"""Utility helpers bridging ORM alerts to realtime channels."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_in_app_broadcast(user_pk: int | None, envelope: dict) -> None:
    if user_pk is None:
        return
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"notify_{user_pk}",
        {"type": "notify.message", "envelope": envelope},
    )


def queue_external_dispatch(notification) -> None:
    """
    Placeholder for celery / sms / whatsapp gateways.
    Call into your provider SDKs inside `apps.integrations.services.dispatchers`.
    """

    try:
        from apps.integrations.services import outbound as outbound_dispatch

        outbound_dispatch.schedule_delivery(notification.id)
    except Exception:  # pragma: no cover - optional integrations
        pass

