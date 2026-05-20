from django.db.models import Q
from django.utils.text import slugify
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsForumAdminOrAbove

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related("milestones", "stakeholder_links")
    serializer_class = ProjectSerializer
    lookup_field = "slug"
    search_fields = ("title", "description", "location")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset().order_by("-created_at")
        user = self.request.user

        params = getattr(self.request, "query_params", {})
        ward = params.get("ward")
        if ward:
            qs = qs.filter(wards_served__icontains=ward)

        thematic = params.get("tag")
        if thematic:
            qs = qs.filter(intervention_tags__icontains=thematic)

        if not user.is_authenticated:
            return qs.exclude(
                status__in=[
                    Project.Status.PENDING,
                    Project.Status.UNDER_REVIEW,
                ]
            )

        role = getattr(user, "role", None)
        if (
            role
            in (
                User.Roles.SUPER_ADMIN,
                User.Roles.FORUM_ADMIN,
            )
            or user.is_superuser
        ):
            return qs

        led_group_ids = user.led_groups.values_list("id", flat=True)
        if role == User.Roles.GROUP_LEADER and led_group_ids.exists():
            return qs.filter(Q(group_id__in=led_group_ids) | Q(steward=user))

        stakeholder_projects = Project.objects.filter(
            stakeholder_links__stakeholder_user=user
        ).values_list("id", flat=True)
        if role == User.Roles.STAKEHOLDER and stakeholder_projects.exists():
            return qs.filter(id__in=stakeholder_projects)

        return qs.exclude(
            status__in=[
                Project.Status.PENDING,
                Project.Status.UNDER_REVIEW,
            ]
        )

    def perform_create(self, serializer):
        title = serializer.validated_data.get("title") or ""
        slug_val = slugify(title)[:200] or "project"
        n = 1
        base = slug_val
        while Project.objects.filter(slug=slug_val).exists():
            n += 1
            slug_val = f"{base}-{n}"
        serializer.save(slug=slug_val, steward=self.request.user)

    @action(
        detail=False,
        permission_classes=[permissions.AllowAny()],
    )
    def kanban(self, request):
        queryset = self.get_queryset()
        board = []
        for value, caption in Project.Status.choices:
            items = queryset.filter(status=value).order_by("-updated_at")[:75]
            board.append(
                {
                    "id": value,
                    "title": caption,
                    "records": ProjectSerializer(items, many=True).data,
                }
            )
        return Response(board)

    @action(
        detail=True,
        permission_classes=[permissions.IsAuthenticated()],
    )
    def timeline(self, request, slug=None):
        project = self.get_object()
        milestones = []
        for milestone in project.milestones.all().order_by("sort_order", "baseline_date"):
            milestones.append(
                {
                    "id": str(milestone.id),
                    "name": milestone.title,
                    "start": milestone.baseline_date.isoformat()
                    if milestone.baseline_date
                    else "",
                    "end": milestone.target_date.isoformat() if milestone.target_date else "",
                    "progress": milestone.completed_date is not None,
                    "ordering": milestone.sort_order,
                }
            )
        return Response(
            {
                "project": project.title,
                "progress": project.progress_percentage,
                "milestones": milestones,
            }
        )

    @action(detail=True, methods=["post"], permission_classes=[IsForumAdminOrAbove()])
    def approve(self, request, slug=None):
        project = self.get_object()
        project.status = Project.Status.APPROVED
        project.progress_percentage = max(project.progress_percentage or 15, 20)
        project.save(update_fields=["status", "progress_percentage", "updated_at"])
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
