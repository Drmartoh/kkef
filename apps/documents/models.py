import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Document(TimeStampedModel):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "Citizen Transparency"
        PARTNER = "partner", "Partner Secure"
        BOARD = "board", "Executive / Board Only"

    class DocType(models.TextChoices):
        POLICY = "policy", "Policy / Constitution"
        FINANCIAL = "financial", "Financial Statement"
        IMPACT = "impact", "Impact Evaluation"
        PROPOSAL_DRAFT = "proposal_draft", "Proposal Working File"
        MEMO = "memo", "Memorandum"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    doc_type = models.CharField(max_length=40, choices=DocType.choices, default=DocType.OTHER)
    visibility = models.CharField(
        max_length=32,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
    )

    group = models.ForeignKey(
        "organizations.CommunityGroup",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="document_registry",
    )
    project = models.ForeignKey(
        "projects.Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="document_registry",
    )
    proposal = models.ForeignKey(
        "proposals.Proposal",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="document_registry",
    )

    file = models.FileField(upload_to="secure_registry/")
    mime_type = models.CharField(max_length=120, blank=True)
    checksum = models.CharField(max_length=128, blank=True)
    digest_sha256 = models.CharField(max_length=64, blank=True)

    version_label = models.CharField(max_length=32, default="v1")
    previous_version = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="derivative_versions",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="documents_uploaded",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="documents_cleared",
        on_delete=models.SET_NULL,
    )

    confidentiality_note = models.TextField(blank=True)
