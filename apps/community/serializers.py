from rest_framework import serializers

from apps.community.models import (
    DiscussionPost,
    DiscussionThread,
    FeedbackSubmission,
    Forum,
    Poll,
    PollOption,
    PollVote,
    Survey,
    SurveySubmission,
)


class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = "__all__"


class DiscussionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionPost
        fields = "__all__"


class DiscussionThreadSerializer(serializers.ModelSerializer):
    posts = DiscussionPostSerializer(many=True, read_only=True)

    class Meta:
        model = DiscussionThread
        fields = "__all__"
        read_only_fields = ("slug",)


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = "__all__"


class PollSerializer(serializers.ModelSerializer):
    choices = PollOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = "__all__"


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = "__all__"


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class SurveySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySubmission
        fields = "__all__"


class FeedbackSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSubmission
        fields = "__all__"
