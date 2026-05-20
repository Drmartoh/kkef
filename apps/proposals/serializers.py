from rest_framework import serializers

from apps.proposals.models import Proposal, ProposalAttachment, ProposalReview


class ProposalAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalAttachment
        fields = "__all__"


class ProposalReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalReview
        fields = "__all__"


class ProposalSerializer(serializers.ModelSerializer):
    attachments = ProposalAttachmentSerializer(many=True, read_only=True)
    reviews = ProposalReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Proposal
        fields = "__all__"
        read_only_fields = ("id", "slug", "created_at", "updated_at")
