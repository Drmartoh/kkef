from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.integrations.views import ManageSnapshotAPI
from apps.manage import viewsets

router = DefaultRouter()
router.register(r"officials", viewsets.ForumOfficialManageViewSet, basename="manage-official")
router.register(r"projects", viewsets.ProjectManageViewSet, basename="manage-project")
router.register(r"project-media", viewsets.ProjectMediaManageViewSet, basename="manage-project-media")
router.register(r"project-milestones", viewsets.ProjectMilestoneManageViewSet, basename="manage-project-milestone")
router.register(r"documents", viewsets.DocumentManageViewSet, basename="manage-document")
router.register(r"groups", viewsets.CommunityGroupManageViewSet, basename="manage-group")
router.register(r"events", viewsets.EventManageViewSet, basename="manage-event")
router.register(r"news", viewsets.NewsArticleManageViewSet, basename="manage-news")
router.register(r"proposals", viewsets.ProposalManageViewSet, basename="manage-proposal")
router.register(r"donor-intakes", viewsets.DonorIntakeManageViewSet, basename="manage-donor-intake")
router.register(
    r"group-applications",
    viewsets.GroupJoinApplicationManageViewSet,
    basename="manage-group-application",
)
router.register(r"donations", viewsets.DonationManageViewSet, basename="manage-donation")
router.register(r"users", viewsets.UserManageViewSet, basename="manage-user")

urlpatterns = [
    path("meta/", viewsets.ManageMetaAPI.as_view(), name="manage-meta"),
    path("snapshot/", ManageSnapshotAPI.as_view(), name="manage-snapshot"),
    path("", include(router.urls)),
]
