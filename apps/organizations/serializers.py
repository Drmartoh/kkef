from rest_framework import serializers

from apps.organizations.models import CommunityGroup, GroupMembership


class CommunityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityGroup
        fields = "__all__"
        read_only_fields = ("id", "slug", "created_at", "updated_at", "members_count_cached", "created_by")


class GroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        exclude = ()
