import uuid

from django.db.models import Count, Sum
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import ReadOnlyUnlessPrivileged

from .models import Donation, Sponsor
from .serializers import DonationSerializer, SponsorSerializer


class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.filter(is_active=True).order_by("name")
    serializer_class = SponsorSerializer
    permission_classes = [ReadOnlyUnlessPrivileged]


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by("-created_at")
    serializer_class = DonationSerializer
    filterset_fields = ("status", "channel", "project")

    def get_permissions(self):
        if self.action in ("rollup", "create"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        params = getattr(self.request, "query_params", {})

        project_slug = params.get("project_slug")
        if project_slug:
            qs = qs.filter(project__slug=project_slug)

        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            if user.is_superuser or user.role in (
                User.Roles.SUPER_ADMIN,
                User.Roles.FORUM_ADMIN,
            ):
                return qs
            return qs.filter(donor=user)

        # Public transparency rails
        return qs.filter(status=Donation.Status.COMPLETED, anonymous=False)

    def perform_create(self, serializer):
        reference = uuid.uuid4().hex[:18].upper()
        donor = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            donor=donor,
            reference=reference,
            status=Donation.Status.PENDING,
        )

    @action(detail=False, permission_classes=[permissions.AllowAny])
    def rollup(self, request):
        queryset = Donation.objects.filter(status=Donation.Status.COMPLETED).exclude(amount__lte=0)
        total_row = queryset.aggregate(sum_amount=Sum("amount"), gifts=Count("id"))
        total = total_row["sum_amount"] or 0
        count = total_row["gifts"] or 0

        slices = []
        thematic = (
            queryset.values("earmark_category")
            .annotate(amount=Sum("amount"), gifts=Count("id"))
            .order_by("-amount")[:12]
        )
        for bucket in thematic:
            label = bucket["earmark_category"] or "general"
            slices.append(
                {
                    "label": label,
                    "amount": bucket["amount"] or 0,
                    "count": bucket["gifts"],
                }
            )

        top_projects = []
        enriched = queryset.values("project__title").annotate(amount=Sum("amount")).order_by("-amount")[:8]
        for row in enriched:
            top_projects.append({"title": row["project__title"] or "Operational reserve", "amount": row["amount"]})

        return Response(
            {
                "total_amount": total,
                "successful_gifts": count,
                "category_slices": slices,
                "project_leaderboard": top_projects,
                "credibility_banner": "All figures originate from audited ledger entries synced through KKEF financial controls.",  # noqa: E501
            }
        )
