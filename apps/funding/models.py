import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Sponsor(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=260, unique=True)
    tier = models.CharField(max_length=64, blank=True)
    logo = models.ImageField(upload_to="sponsors/", blank=True)
    headline = models.TextField(blank=True)
    thematic_alignment = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    liaison_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="managed_sponsors",
    )

    def __str__(self) -> str:
        return self.name


class Donation(TimeStampedModel):
    class Channel(models.TextChoices):
        CARD = "card", "Stripe / Card"
        PAYPAL = "paypal", "PayPal"
        MPESA = "mpesa", "M-Pesa"
        BANK = "bank", "Bank / Cheque"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Settled"
        FAILED = "failed", "Failed / Reversed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=64, blank=True)

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pledges_recorded",
    )
    donor_display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    tribute_message = models.TextField(blank=True)

    sponsor = models.ForeignKey(
        Sponsor,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="hosted_donations",
    )

    project = models.ForeignKey(
        "projects.Project",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="donations_allocated",
    )
    earmark_category = models.CharField(max_length=120, blank=True)

    currency = models.CharField(max_length=8, default="KES")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    anonymous = models.BooleanField(default=False)

    channel = models.CharField(max_length=32, choices=Channel.choices, default=Channel.CARD)

    paypal_order_id = models.CharField(max_length=96, blank=True)
    stripe_session_id = models.CharField(max_length=128, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=128, blank=True)

    mpesa_checkout_request_id = models.CharField(max_length=128, blank=True)
    mpesa_receipt = models.CharField(max_length=64, blank=True)

    ledger_note = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    disbursement_proof = models.FileField(upload_to="donation_proofs/", blank=True)


class DonorIntake(TimeStampedModel):
    """
    Public donor / partner submissions: money, in-kind resources, or letters & proposals.
    Separate from ledger `Donation` rows until finance confirms settlement.
    """

    class Kind(models.TextChoices):
        MONEY = "money", "Financial contribution"
        RESOURCES = "resources", "In-kind resources (sports, farming, trees, etc.)"
        MESSAGE = "message", "Letter, proposal, or written inquiry"

    class ResourceCategory(models.TextChoices):
        SPORTS = "sports", "Sports & recreation"
        FARMING = "farming", "Farming & agriculture"
        TREES = "trees", "Trees, seedlings & re-greening"
        EDUCATION = "education", "Education & literacy"
        HEALTH = "health", "Health & sanitation"
        WATER = "water", "Water & irrigation"
        YOUTH = "youth", "Youth programmes"
        WOMEN = "women", "Women’s empowerment"
        GENERAL = "general", "General / mixed in-kind"

    reference = models.CharField(max_length=24, unique=True, db_index=True, editable=False)
    kind = models.CharField(max_length=32, choices=Kind.choices, db_index=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="KES")
    payment_preference = models.CharField(
        max_length=64,
        blank=True,
        help_text="e.g. M-Pesa, bank, card, will follow up",
    )

    resource_category = models.CharField(
        max_length=32,
        choices=ResourceCategory.choices,
        blank=True,
    )
    resource_description = models.TextField(blank=True)
    quantity_or_estimate = models.CharField(max_length=255, blank=True)

    message_subject = models.CharField(max_length=255, blank=True)
    message_body = models.TextField(blank=True)
    attachment = models.FileField(upload_to="donor_intake_attachments/", blank=True)

    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    anonymous = models.BooleanField(
        default=False,
        help_text="If true, name is withheld from public honour rolls; KKEF may still contact you privately.",
    )

    email_to_team_sent_at = models.DateTimeField(null=True, blank=True)
    staff_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            import secrets

            for _ in range(32):
                candidate = f"DI-{secrets.token_hex(4).upper()}"
                if not DonorIntake.objects.filter(reference=candidate).exists():
                    self.reference = candidate
                    break
            else:
                self.reference = f"DI-{secrets.token_hex(8).upper()}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.reference} ({self.get_kind_display()})"
