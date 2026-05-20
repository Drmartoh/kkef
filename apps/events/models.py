import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class EventQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(start_at__gte=timezone.now() - timedelta(minutes=5)).order_by("start_at")

    def past(self):
        return self.filter(end_at__lt=timezone.now()).order_by("-end_at")


class Event(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=260, blank=True)
    organizer_group = models.ForeignKey(
        "organizations.CommunityGroup",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organized_events",
    )
    stewardship_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hosted_events",
    )

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    thematic_track = models.CharField(max_length=120, blank=True)

    narrative = models.TextField(blank=True)
    agendas = models.TextField(blank=True)

    hero_image = models.ImageField(upload_to="event_covers/", blank=True)

    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField()

    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    venue_descriptor = models.CharField(max_length=255, blank=True)

    ticketing_enabled = models.BooleanField(default=False)
    ticketing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ticketing_currency = models.CharField(max_length=8, default="KES")

    capacity = models.PositiveIntegerField(null=True, blank=True)
    public_qr_seed = models.CharField(max_length=120, blank=True)

    reminders_email = models.BooleanField(default=True)
    reminders_sms = models.BooleanField(default=False)

    is_public = models.BooleanField(default=True, db_index=True)
    volunteering_open = models.BooleanField(default=False)

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ["start_at"]

    def __str__(self) -> str:
        return self.title


class EventTicket(TimeStampedModel):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        REDEEMED = "redeemed", "Redeemed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, related_name="tickets", on_delete=models.CASCADE)
    holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="issued_tickets",
    )
    display_name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=64, db_index=True, unique=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ISSUED)
    redeemed_at = models.DateTimeField(null=True, blank=True)


class RSVP(TimeStampedModel):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Confirmed"
        WAITLISTED = "waitlisted", "Waitlisted"
        DECLINED = "declined", "Declined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, related_name="rsvp_entries", on_delete=models.CASCADE)
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rsvp_history",
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.RESERVED)
    companions = models.PositiveSmallIntegerField(default=0)
    dietary_notes = models.CharField(max_length=160, blank=True)

    class Meta:
        unique_together = ("event", "attendee")


class EventPhoto(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="event_archive/")
    caption = models.CharField(max_length=255, blank=True)
    attribution = models.CharField(max_length=160, blank=True)
