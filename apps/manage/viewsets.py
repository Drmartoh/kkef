from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.core.kiambu_data import GROUP_APPLICATION_TYPE_CHOICES, KIAMBU_WARD_CHOICES
from apps.core.models import ForumOfficial
from apps.documents.models import Document
from apps.events.models import Event
from apps.funding.models import Donation, DonorIntake
from apps.manage.permissions import IsManageOperator
from apps.manage.serializers import (
    CommunityGroupManageSerializer,
    DocumentManageSerializer,
    DonationManageSerializer,
    DonorIntakeManageSerializer,
    EventManageSerializer,
    ForumOfficialManageSerializer,
    GroupJoinApplicationManageSerializer,
    NewsArticleManageSerializer,
    ProjectManageSerializer,
    ProjectMediaManageSerializer,
    ProjectMilestoneManageSerializer,
    ProposalManageSerializer,
    UserManageSerializer,
)
from apps.media_center.models import NewsArticle
from apps.organizations.models import CommunityGroup, GroupJoinApplication
from apps.projects.models import Project, ProjectMedia, ProjectMilestone
from apps.proposals.models import Proposal


class ManageParserMixin:
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ManageMetaAPI(APIView):
    permission_classes = [IsManageOperator]

    def get(self, request):
        groups = list(
            CommunityGroup.objects.order_by("name").values("id", "name", "slug", "is_published")[:500]
        )
        users = list(
            User.objects.filter(is_active=True)
            .order_by("username")
            .values("id", "username", "first_name", "last_name", "role")[:200]
        )
        projects = list(
            Project.objects.order_by("-updated_at").values("id", "title", "status")[:300]
        )
        proposals = list(
            Proposal.objects.order_by("-updated_at").values("id", "title", "status")[:200]
        )
        return Response(
            {
                "project_statuses": [
                    {"value": v, "label": l} for v, l in Project.Status.choices
                ],
                "proposal_statuses": [
                    {"value": v, "label": l} for v, l in Proposal.Status.choices
                ],
                "news_statuses": [
                    {"value": v, "label": l} for v, l in NewsArticle.Status.choices
                ],
                "official_tiers": [
                    {"value": v, "label": l} for v, l in ForumOfficial.Tier.choices
                ],
                "group_types": [
                    {"value": v, "label": l} for v, l in CommunityGroup.GroupType.choices
                ],
                "group_application_statuses": [
                    {"value": v, "label": l} for v, l in GroupJoinApplication.Status.choices
                ],
                "donor_intake_kinds": [
                    {"value": v, "label": l} for v, l in DonorIntake.Kind.choices
                ],
                "donation_statuses": [
                    {"value": v, "label": l} for v, l in Donation.Status.choices
                ],
                "document_types": [
                    {"value": v, "label": l} for v, l in Document.DocType.choices
                ],
                "document_visibility": [
                    {"value": v, "label": l} for v, l in Document.Visibility.choices
                ],
                "wards": [{"value": v, "label": l} for v, l in KIAMBU_WARD_CHOICES],
                "application_group_types": [
                    {"value": v, "label": l} for v, l in GROUP_APPLICATION_TYPE_CHOICES
                ],
                "groups": groups,
                "projects": projects,
                "proposals": proposals,
                "users": users,
            }
        )


class ForumOfficialManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = ForumOfficial.objects.all()
    serializer_class = ForumOfficialManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("name", "role")


class ProjectManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = Project.objects.select_related("group").prefetch_related("media_items", "milestones")
    serializer_class = ProjectManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("title", "description", "location", "intervention_tags")

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        project = self.get_object()
        project.status = Project.Status.ONGOING
        if project.progress_percentage < 10:
            project.progress_percentage = 15
        project.save(update_fields=["status", "progress_percentage", "updated_at"])
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        project = self.get_object()
        project.status = Project.Status.UNDER_REVIEW
        project.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(project).data)


class ProjectMilestoneManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    serializer_class = ProjectMilestoneManageSerializer
    permission_classes = [IsManageOperator]

    def get_queryset(self):
        qs = ProjectMilestone.objects.select_related("project")
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.order_by("sort_order", "baseline_date")


class ProjectMediaManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    serializer_class = ProjectMediaManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("caption", "tags")

    def get_queryset(self):
        qs = ProjectMedia.objects.select_related("project")
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.order_by("sort_order", "-created_at")


class CommunityGroupManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = CommunityGroup.objects.all()
    serializer_class = CommunityGroupManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("name", "ward", "summary")


class EventManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = Event.objects.select_related("organizer_group")
    serializer_class = EventManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("title", "summary", "venue_descriptor")


class NewsArticleManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("title", "summary", "tags_csv")

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.status = NewsArticle.Status.PUBLISHED
        article.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(article).data)


class ProposalManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = Proposal.objects.select_related("owning_group")
    serializer_class = ProposalManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("title", "synopsis", "reference")


class DocumentManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = Document.objects.select_related("group", "project", "proposal")
    serializer_class = DocumentManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("title", "confidentiality_note", "version_label")


class DonorIntakeManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = DonorIntake.objects.all()
    serializer_class = DonorIntakeManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("reference", "display_name", "email", "phone")
    http_method_names = ["get", "patch", "delete", "head", "options"]


class GroupJoinApplicationManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = GroupJoinApplication.objects.all()
    serializer_class = GroupJoinApplicationManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("group_name", "certificate_number", "chairperson_name")
    lookup_field = "certificate_number"


class DonationManageViewSet(ManageParserMixin, viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("reference",)
    http_method_names = ["get", "patch", "delete", "head", "options"]


class UserManageViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserManageSerializer
    permission_classes = [IsManageOperator]
    search_fields = ("username", "email", "first_name", "last_name")
    http_method_names = ["get", "patch", "head", "options"]
