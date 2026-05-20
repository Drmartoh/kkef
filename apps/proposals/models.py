import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Proposal(TimeStampedModel):
    class Category(models.TextChoices):
        ENVIRONMENT = "environment", "Environment & Climate Action"
        YOUTH = "youth", "Youth Empowerment"
        AGRICULTURE = "agriculture", "Agriculture & Food Systems"
        FISH_FARMING = "fish_farming", "Aquaculture / Fish Farming"
        WOMEN = "women", "Women Empowerment"
        CLEANUP = "cleanup", "Community Clean-Up"
        EDUCATION = "education", "Education & Literacy"
        WATER = "water", "Water Projects"
        HEALTH = "health", "Community Health"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Stakeholder Queue"
        AWAITING_APPROVAL = "awaiting_approval", "Awaiting Executive Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Returned for Revision"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=32, blank=True, db_index=True)
    slug = models.SlugField(max_length=260, blank=True)

    owning_group = models.ForeignKey(
        "organizations.CommunityGroup",
        on_delete=models.CASCADE,
        related_name="proposals",
    )
    authored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="authored_proposals",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=40, choices=Category.choices, db_index=True)
    synopsis = models.TextField()
    rationale = models.TextField(blank=True)
    implementation_plan = models.TextField(blank=True)
    risk_register = models.TextField(blank=True)

    projected_budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cofunding_commitments = models.TextField(blank=True)

    beneficiaries_estimate = models.PositiveIntegerField(default=0)
    sdg_tags = models.JSONField(default=list, blank=True)

    template_key = models.CharField(max_length=120, blank=True)
    ai_draft_hints = models.TextField(blank=True)

    status = models.CharField(
        max_length=48,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    stakeholder_deadline_at = models.DateTimeField(null=True, blank=True)
    finalized_pdf = models.FileField(upload_to="proposal_exports/", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class ProposalAttachment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="proposal_documents/")
    label = models.CharField(max_length=160, blank=True)
    mime_type = models.CharField(max_length=120, blank=True)
    checksum = models.CharField(max_length=128, blank=True)


class ProposalReview(TimeStampedModel):
    class Decision(models.TextChoices):
        IN_PROGRESS = "in_progress", "Commentary"
        ENDORSED = "endorsed", "Endorsed"
        FLAGGED = "flagged", "Flagged Risks"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposal_reviews_performed",
    )
    stakeholder_label = models.CharField(max_length=160, blank=True)
    commentary = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    decision = models.CharField(max_length=32, choices=Decision.choices)

    digitally_signed_manifest = models.TextField(blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    confidentiality_level = models.CharField(max_length=64, blank=True)


class ProposalDigitalSignature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, related_name="signatures", on_delete=models.CASCADE)
    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    role_label = models.CharField(max_length=120)
    signature_blob = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
