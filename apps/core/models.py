import uuid

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract created/updated timestamps for traceability."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ForumOfficial(TimeStampedModel):
    """Leadership roster — portraits and bios managed via Django admin."""

    class Tier(models.TextChoices):
        EXECUTIVE = "executive", "Executive board"
        EXTENDED = "extended", "Extended secretariat"

    tier = models.CharField(max_length=16, choices=Tier.choices, db_index=True)
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=120)
    tagline = models.CharField(max_length=200, blank=True)
    bio = models.TextField()
    tenure = models.CharField(max_length=200, blank=True)
    focus_areas = models.JSONField(default=list, blank=True)
    photo = models.ImageField(upload_to="officials/%Y/%m/", blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["tier", "sort_order", "name"]
        verbose_name = "forum official"
        verbose_name_plural = "forum officials"

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"

    def save(self, *args, **kwargs):
        reprocess = kwargs.pop("reprocess_photo", False)
        if self.photo:
            should_process = reprocess
            if not should_process and self.pk:
                previous = (
                    ForumOfficial.objects.filter(pk=self.pk)
                    .values_list("photo", flat=True)
                    .first()
                )
                should_process = str(previous or "") != str(self.photo)
            elif not self.pk:
                should_process = True

            if should_process:
                from apps.core.official_images import normalize_official_photo

                normalized = normalize_official_photo(self.photo)
                if normalized:
                    self.photo.save(normalized.name, normalized, save=False)

        super().save(*args, **kwargs)

    @property
    def photo_url(self) -> str:
        if self.photo:
            return self.photo.url
        from apps.core.officials import placeholder_avatar

        return placeholder_avatar(self.name)


class AuditLog(models.Model):
    """Structured audit trail for institutional transparency."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    action = models.CharField(max_length=64)
    path = models.CharField(max_length=512, blank=True)
    method = models.CharField(max_length=8, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]
