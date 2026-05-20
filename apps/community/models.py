import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Forum(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=170, unique=True)
    synopsis = models.TextField(blank=True)
    moderated = models.BooleanField(default=True)


class DiscussionThread(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forum = models.ForeignKey(Forum, related_name="threads", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="authored_discussions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    pinned = models.BooleanField(default=False, db_index=True)
    excerpt = models.TextField(blank=True)


class DiscussionPost(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(DiscussionThread, related_name="posts", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    reply_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    body = models.TextField()


class Poll(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    context = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    multi_select_allowed = models.BooleanField(default=False)
    closes_at = models.DateTimeField(null=True, blank=True)


class PollOption(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, related_name="choices", on_delete=models.CASCADE)
    label = models.CharField(max_length=255)


class PollVote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    option = models.ForeignKey(PollOption, related_name="ballots", on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("option", "voter")


class Survey(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    synopsis = models.TextField(blank=True)
    questionnaire = models.JSONField(default=dict)
    is_open = models.BooleanField(default=True)


class SurveySubmission(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, related_name="responses", on_delete=models.CASCADE)
    submitter_email = models.EmailField(blank=True)
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="survey_submissions",
    )
    payload = models.JSONField(default=dict)


class FeedbackSubmission(TimeStampedModel):
    class Category(models.TextChoices):
        SERVICES = "services", "Citizen Experience"
        ENVIRONMENT = "environment", "Environment"
        VOLUNTEER = "volunteer", "Volunteer Experience"
        OTHER = "other", "General"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=64, choices=Category.choices, default=Category.OTHER)
    message = models.TextField()
    contact_email = models.EmailField(blank=True)
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="feedback_shared",
    )
