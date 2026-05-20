from django.utils.text import slugify
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsForumAdminOrAbove
from apps.organizations.serializers import CommunityGroupSerializer

from .models import CommunityGroup, GroupMembership


class CommunityGroupViewSet(viewsets.ModelViewSet):
    queryset = CommunityGroup.objects.all().order_by("name")
    serializer_class = CommunityGroupSerializer
    lookup_field = "slug"
    search_fields = ("name", "summary", "thematic_focus_tags", "registration_number")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]

    def perform_create(self, serializer):
        name = serializer.validated_data.get("name") or ""
        slug_base = slugify(name)[:200] or "group"
        slug_val = slug_base
        n = 1
        while CommunityGroup.objects.filter(slug=slug_val).exists():
            n += 1
            slug_val = f"{slug_base}-{n}"
        serializer.save(slug=slug_val, created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated()])
    def request_membership(self, request, slug=None):
        group = self.get_object()
        if request.user.role not in (
            User.Roles.MEMBER,
            User.Roles.GROUP_LEADER,
            User.Roles.STAKEHOLDER,
            User.Roles.DONOR,
        ):
            return Response({"detail": "Role not permitted."}, status=status.HTTP_403_FORBIDDEN)
        gm, created = GroupMembership.objects.get_or_create(
            user=request.user,
            group=group,
            defaults={"verified": False},
        )
        return Response({"created": created, "membership_id": str(gm.id)})
