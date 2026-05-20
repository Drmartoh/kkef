from django.db.models import Count
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import ReadOnlyUnlessPrivileged

from .models import DiscussionPost, DiscussionThread, FeedbackSubmission, Forum, Poll, PollVote, Survey
from .serializers import (
    DiscussionPostSerializer,
    DiscussionThreadSerializer,
    FeedbackSubmissionSerializer,
    ForumSerializer,
    PollSerializer,
    SurveySerializer,
    SurveySubmissionSerializer,
)


class ForumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Forum.objects.prefetch_related("threads").all().order_by("name")
    serializer_class = ForumSerializer


class DiscussionThreadViewSet(viewsets.ModelViewSet):
    queryset = DiscussionThread.objects.prefetch_related("posts").all().order_by("-pinned", "-updated_at")
    serializer_class = DiscussionThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from django.utils.text import slugify

        title = serializer.validated_data.get("title") or "conversation"
        slug_val = slugify(title)[:200] or "thread"
        n = 1
        base = slug_val
        while DiscussionThread.objects.filter(slug=slug_val).exists():
            n += 1
            slug_val = f"{base}-{n}"
        serializer.save(author=self.request.user, slug=slug_val)


class DiscussionPostViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = DiscussionPost.objects.select_related("thread").order_by("created_at")
        thread_slug = getattr(self.request, "query_params", {}).get("thread")
        if thread_slug:
            queryset = queryset.filter(thread__slug=thread_slug)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.prefetch_related("choices").order_by("-created_at")
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    class VotePayloadSerializer(serializers.Serializer):
        option = serializers.UUIDField()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated()])
    def vote(self, request, pk=None):
        poll = self.get_object()
        payload = self.VotePayloadSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        choice_id = payload.validated_data["option"]
        choice = poll.choices.filter(pk=choice_id).first()
        if not choice:
            return Response({"detail": "Invalid ballot."}, status=status.HTTP_400_BAD_REQUEST)

        if not poll.multi_select_allowed and PollVote.objects.filter(
            voter=request.user,
            option__poll=poll,
        ).exists():
            return Response({"detail": "Vote already logged."}, status=status.HTTP_400_BAD_REQUEST)

        PollVote.objects.get_or_create(option=choice, voter=request.user)

        tallies = (
            poll.choices.annotate(ballots=Count("ballots")).values("label", "id", "ballots").order_by("-ballots")  # noqa: E501
        )
        return Response({"computed_tally": list(tallies)}, status=status.HTTP_201_CREATED)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = FeedbackSubmission.objects.all().order_by("-created_at")
    serializer_class = FeedbackSubmissionSerializer
    http_method_names = ["post", "get", "options", "head"]
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)
        serializer.save(respondent=user if getattr(user, "is_authenticated", False) else None)


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all().order_by("-created_at")
    serializer_class = SurveySerializer
    permission_classes = [ReadOnlyUnlessPrivileged]

    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def respond(self, request, pk=None):
        survey = self.get_object()
        payload = SurveySubmissionSerializer(
            data={**request.data, "survey": str(survey.id)},
        )
        payload.is_valid(raise_exception=True)
        user = getattr(request, "user", None)
        payload.save(respondent=user if getattr(user, "is_authenticated", False) else None)
        return Response(payload.data, status=status.HTTP_201_CREATED)
