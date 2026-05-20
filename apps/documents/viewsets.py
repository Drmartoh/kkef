from django.utils.text import slugify
from rest_framework import permissions, viewsets

from apps.accounts.models import User
from apps.accounts.permissions import IsForumAdminOrAbove

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.order_by("-created_at")
    serializer_class = DocumentSerializer

    def get_permissions(self):
        user = getattr(self.request, "user", None)

        if self.request.method == "OPTIONS":
            return [permissions.AllowAny()]

        if self.request.method in permissions.SAFE_METHODS:
            if user and (
                user.is_superuser or user.role in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN)
            ):
                return [permissions.IsAuthenticated()]
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)

        project_slug = getattr(self.request, "query_params", {}).get("project")
        if project_slug:
            qs = qs.filter(project__slug=project_slug)

        if user and user.is_authenticated and (
            user.is_superuser or user.role in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN)
        ):
            return qs

        return qs.filter(visibility=Document.Visibility.PUBLIC)

    def perform_create(self, serializer):
        title = serializer.validated_data.get("title") or "document"
        slug_val = slugify(title)[:200] or "document"
        n = 1
        base = slug_val
        while Document.objects.filter(slug=slug_val).exists():
            n += 1
            slug_val = f"{base}-{n}"
        serializer.save(slug=slug_val, uploaded_by=self.request.user)
