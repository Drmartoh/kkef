from rest_framework import serializers

from apps.projects.models import (
    KanbanLane,
    KanbanMembership,
    Project,
    ProjectMilestone,
    ProjectStakeholder,
)


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = "__all__"


class ProjectStakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStakeholder
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    stakeholders = ProjectStakeholderSerializer(
        many=True, read_only=True, source="stakeholder_links"
    )

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class KanbanLaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanLane
        fields = "__all__"


class KanbanMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanMembership
        fields = "__all__"
