from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.models import Notification
from apps.notifications.utils import push_in_app_broadcast, queue_external_dispatch


@receiver(post_save, sender=Notification)
def notification_delivery(sender, instance, created, **kwargs):  # noqa: ARG001
    if not created:
        return

    envelope = {
        "id": str(instance.id),
        "title": instance.title,
        "verb": instance.verb,
        "channel": instance.channel,
        "created_at": instance.created_at.isoformat(),
    }

    push_in_app_broadcast(instance.recipient_id, envelope)
    queue_external_dispatch(instance)

