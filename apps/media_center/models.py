import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class PhotoGallery(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True)
    synopsis = models.TextField(blank=True)
    thematic_tag = models.CharField(max_length=120, blank=True)
    curator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )


class GalleryImage(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery = models.ForeignKey(PhotoGallery, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media_galleries/")
    caption = models.CharField(max_length=255, blank=True)
    photographer = models.CharField(max_length=160, blank=True)


class VideoAsset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True)
    synopsis = models.TextField(blank=True)
    external_url = models.URLField(blank=True)
    cover = models.ImageField(upload_to="video_covers/", blank=True)


class NewsArticle(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True)
    summary = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="newsroom/", blank=True)
    body = models.TextField()
    spotlight_quote = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)

    authored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_assets",
    )
    tags_csv = models.CharField(max_length=255, blank=True)


class PressRelease(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headline = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True)
    summary = models.TextField(blank=True)
    downloadable = models.FileField(upload_to="press_pdf/", blank=True)
    embargo_until = models.DateTimeField(blank=True, null=True)
