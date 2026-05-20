from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import MeRetrieveUpdateAPIView
from apps.community.viewsets import (
    DiscussionPostViewSet,
    DiscussionThreadViewSet,
    FeedbackViewSet,
    ForumViewSet,
    PollViewSet,
    SurveyViewSet,
)
from apps.documents.viewsets import DocumentViewSet
from apps.events.viewsets import EventViewSet
from apps.funding.viewsets import DonationViewSet, SponsorViewSet
from apps.integrations import views as toolbox_views
from apps.integrations import views_ai
from apps.media_center.viewsets import (
    GalleryImageViewSet,
    NewsArticleViewSet,
    PhotoGalleryViewSet,
    PressReleaseViewSet,
    VideoAssetViewSet,
)
from apps.notifications.viewsets import NotificationViewSet
from apps.organizations.viewsets import CommunityGroupViewSet
from apps.projects.viewsets import ProjectViewSet
from apps.proposals.viewsets import ProposalViewSet

router = DefaultRouter()
router.register(r"orgs/groups", CommunityGroupViewSet, basename="org-group")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"proposals", ProposalViewSet, basename="proposal")
router.register(r"funding/sponsors", SponsorViewSet, basename="sponsor")
router.register(r"funding/donations", DonationViewSet, basename="donation")
router.register(r"events", EventViewSet, basename="event")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"media/galleries", PhotoGalleryViewSet, basename="gallery")
router.register(r"media/gallery-images", GalleryImageViewSet, basename="gallery-image")
router.register(r"media/videos", VideoAssetViewSet, basename="video")
router.register(r"media/news", NewsArticleViewSet, basename="news")
router.register(r"media/press", PressReleaseViewSet, basename="press")
router.register(r"community/forums", ForumViewSet, basename="forum")
router.register(r"community/threads", DiscussionThreadViewSet, basename="thread")
router.register(r"community/posts", DiscussionPostViewSet, basename="discussion-post")
router.register(r"community/polls", PollViewSet, basename="poll")
router.register(r"community/feedback", FeedbackViewSet, basename="feedback")
router.register(r"community/surveys", SurveyViewSet, basename="survey")
router.register(r"notifications/inbox", NotificationViewSet, basename="notification")


urlpatterns = [
    path("", include(router.urls)),
    path("me/", MeRetrieveUpdateAPIView.as_view(), name="api-me"),
    path("analytics/tiles/", toolbox_views.TransparencyTilesAPI.as_view()),
    path("analytics/executive/", toolbox_views.ExecutiveObservatoryAPI.as_view()),
    path("proposal/export/pdf/", toolbox_views.ProposalPdfExportStub.as_view()),
    path(
        "payments/bootstrap/",
        toolbox_views.payment_session_stub,
        name="payments-bootstrap",
    ),
    path(
        "ai/proposal-draft/",
        views_ai.ProposalDraftAssistantAPI.as_view(),
        name="ai-proposal-draft",
    ),
    path(
        "ai/report-summary/",
        views_ai.ReportSummarizerAPI.as_view(),
        name="ai-report-summary",
    ),
    path(
        "ai/chatbot/",
        views_ai.CommunityChatbotAPI.as_view(),
        name="ai-chatbot",
    ),
    path(
        "ai/recommendations/",
        views_ai.RecommendationEngineAPI.as_view(),
        name="ai-recommendations",
    ),
]
