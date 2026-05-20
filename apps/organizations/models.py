import uuid

from django.conf import settings
from django.db import models

from apps.core.kiambu_data import GROUP_APPLICATION_TYPE_CHOICES, KIAMBU_WARD_CHOICES
from apps.core.models import TimeStampedModel


class CommunityGroup(TimeStampedModel):
    """Umbrella sub-organization: CBO, SACCOs, thematic clusters, etc."""

    class GroupType(models.TextChoices):
        CBO = "cbo", "Community Based Organization"
        YOUTH = "youth", "Youth Forum / Group"
        WOMEN = "women", "Women Group"
        SACCO = "sacco", "SACCO / Financial Collective"
        ENVIRONMENT = "environment", "Environmental Group"
        FISH_FARMERS = "fish_farmers", "Fish Farmers"
        STAKEHOLDER = "stakeholder", "Stakeholder Cell"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    group_type = models.CharField(max_length=40, choices=GroupType.choices)
    motto = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to="group_logos/", blank=True)
    registration_number = models.CharField(max_length=120, blank=True)
    registration_authority = models.CharField(max_length=160, blank=True)
    founded_on = models.DateField(null=True, blank=True)
    county = models.CharField(max_length=120, default="Kiambu")
    ward = models.CharField(max_length=120, blank=True)
    location_notes = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    summary = models.TextField(blank=True)
    narrative = models.TextField(blank=True)

    chairs_message = models.TextField(blank=True)
    secretary_name = models.CharField(max_length=160, blank=True)
    treasurer_name = models.CharField(max_length=160, blank=True)

    members_count_cached = models.PositiveIntegerField(default=0)

    leaders = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="led_groups",
        help_text="Designated coordinators with elevated group permissions.",
    )

    partner_organizations = models.TextField(blank=True)
    thematic_focus_tags = models.CharField(max_length=255, blank=True)

    annual_budget_estimate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registered_groups",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class GroupJoinApplication(TimeStampedModel):
    """
    Groups apply to join the forum. Certificate / registration number is the natural key
    so duplicate applications are rejected at the database level.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        UNDER_REVIEW = "under_review", "Under review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Not admitted"
        DUPLICATE = "duplicate", "Closed — duplicate"

    certificate_number = models.CharField(
        max_length=120,
        primary_key=True,
        help_text="Official registration or certificate number — must be unique.",
    )
    group_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    chairperson_name = models.CharField(
        max_length=160,
        help_text="Chairperson or primary contact person",
    )
    group_type = models.CharField(max_length=64, choices=GROUP_APPLICATION_TYPE_CHOICES)
    ward = models.CharField(max_length=64, choices=KIAMBU_WARD_CHOICES)
    contact_email = models.EmailField(blank=True)

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    email_to_team_sent_at = models.DateTimeField(null=True, blank=True)
    secretariat_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Group join application"
        verbose_name_plural = "Group join applications"

    def __str__(self) -> str:
        return f"{self.group_name} ({self.certificate_number})"


class GroupMembership(TimeStampedModel):
    class MemberRoles(models.TextChoices):
        CORE_MEMBER = "core_member", "Core Member"
        PATRON = "patron", "Patron"
        VOLUNTEER = "volunteer", "Volunteer"
        BENEFICIARY_REP = "beneficiary_rep", "Beneficiary Representative"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=48, choices=MemberRoles.choices, default=MemberRoles.CORE_MEMBER)
    verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "group")
