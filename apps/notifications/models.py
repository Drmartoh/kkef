import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "Portal"
        EMAIL = "email", "Electronic Mail"
        SMS = "sms", "SMS Gateway"
        WHATSAPP = "whatsapp", "WhatsApp Outreach"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inbox_notifications",
    )
    channel = models.CharField(max_length=32, choices=Channel.choices, default=Channel.IN_APP)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    verb = models.CharField(max_length=64, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(blank=True, null=True)


class OutreachTemplate(TimeStampedModel):
    key = models.SlugField(max_length=96, unique=True)
    sms_copy = models.TextField(blank=True)
    whatsapp_copy = models.TextField(blank=True)
