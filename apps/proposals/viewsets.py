from django.db.models import Q
from django.utils.text import slugify
from rest_framework import permissions, viewsets

from apps.accounts.models import User

from .models import Proposal
from .serializers import ProposalSerializer


def _is_forum_leader(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN)))  # noqa: E501


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.prefetch_related("attachments", "reviews").all().order_by(
        "-updated_at"
    )
    serializer_class = ProposalSerializer
    lookup_field = "slug"
    search_fields = ("title", "synopsis", "implementation_plan")

    def get_permissions(self):
        """
        Transparency default: drafts hidden from anonymous callers.
        Group leaders steward their authoring pipeline; admins manage escalation.
        """
        method = getattr(self.request, "method", "GET").upper()
        user = getattr(self.request, "user", None)

        if method == "OPTIONS":
            return [permissions.AllowAny()]

        if method == "GET" and self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]

        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)

        owning = self.request.query_params.get("group")
        if owning:
            qs = qs.filter(owning_group__slug=owning)

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)

        if not user or not user.is_authenticated:
            return qs.exclude(status=Proposal.Status.DRAFT)

        if _is_forum_leader(user):
            return qs

        if user.role == User.Roles.STAKEHOLDER:
            return qs.filter(
                status__in=[
                    Proposal.Status.SUBMITTED,
                    Proposal.Status.UNDER_REVIEW,
                    Proposal.Status.AWAITING_APPROVAL,
                ]
            )

        if user.role == User.Roles.GROUP_LEADER:
            led_ids = user.led_groups.values_list("id", flat=True)
            if led_ids:
                qs = qs.filter(Q(owning_group_id__in=led_ids) | Q(authored_by=user))
                return qs
            return qs.filter(authored_by=user)

        return qs.filter(authored_by=user)

    def perform_create(self, serializer):
        slug_val = slugify(serializer.validated_data["title"])[:220] or "proposal"
        base = slug_val
        n = 1
        while Proposal.objects.filter(slug=slug_val).exists():
            slug_val = f"{base}-{n}"
            n += 1
        serializer.save(slug=slug_val, authored_by=self.request.user)
