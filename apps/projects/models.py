import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Project(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_code = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)

    group = models.ForeignKey(
        "organizations.CommunityGroup",
        related_name="projects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField(blank=True)
    problem_statement = models.TextField(blank=True)
    anticipated_outcomes = models.TextField(blank=True)

    budget_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    funding_secured = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    timeline_start = models.DateField(null=True, blank=True)
    timeline_end = models.DateField(null=True, blank=True)

    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    wards_served = models.CharField(max_length=255, blank=True)

    sdg_goals = models.JSONField(default=list, blank=True)
    beneficiaries_count = models.PositiveIntegerField(default=0)

    intervention_tags = models.CharField(max_length=400, blank=True)
    transparency_summary = models.TextField(blank=True)

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    progress_percentage = models.PositiveSmallIntegerField(default=0)

    cover_image = models.ImageField(upload_to="project_media/", blank=True)
    spotlight_video_url = models.URLField(blank=True)

    steward = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="steward_projects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_public(self) -> bool:
        return self.status not in (self.Status.PENDING, self.Status.UNDER_REVIEW, self.Status.REJECTED)


class ProjectMedia(TimeStampedModel):
    """Gallery images and media attachments for a project."""

    class MediaType(models.TextChoices):
        PHOTO = "photo", "Photo"
        VIDEO = "video", "Video link"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name="media_items", on_delete=models.CASCADE)
    media_type = models.CharField(max_length=16, choices=MediaType.choices, default=MediaType.PHOTO)
    image = models.ImageField(upload_to="project_media/gallery/", blank=True)
    video_url = models.URLField(blank=True)
    caption = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    taken_on = models.DateField(null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.project.title} · {self.caption or self.media_type}"


class ProjectStakeholder(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name="stakeholder_links", on_delete=models.CASCADE)
    stakeholder_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="stakeholding_projects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    external_name = models.CharField(max_length=255, blank=True)
    role_label = models.CharField(max_length=160)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
        ]


class ProjectMilestone(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name="milestones", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    narrative = models.TextField(blank=True)
    baseline_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)

    sort_order = models.PositiveSmallIntegerField(default=0)


class KanbanLane(TimeStampedModel):
    """
    Cosmetic lane presets for thematic boards — projects still own authoritative status fields.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=96, unique=True)
    caption = models.CharField(max_length=160)
    color_token = models.CharField(max_length=32, blank=True)


class KanbanMembership(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(Project, related_name="kanban_card", on_delete=models.CASCADE)
    lane = models.ForeignKey(KanbanLane, on_delete=models.CASCADE)
