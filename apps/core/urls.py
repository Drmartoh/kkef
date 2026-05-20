from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("impact/", views.ImpactView.as_view(), name="impact"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("portal/projects/", views.ProjectsPortalView.as_view(), name="projects_portal"),
    path("portal/groups/", views.GroupsPortalView.as_view(), name="groups_portal"),
    path("portal/events/", views.EventsPortalView.as_view(), name="events_portal"),
    path("portal/media/", views.MediaPortalView.as_view(), name="media_portal"),
    path("portal/maps/", views.MapsPortalView.as_view(), name="maps_portal"),
    path("portal/donate/", views.DonatePortalView.as_view(), name="donate_portal"),
    path("portal/proposals/", views.ProposalsPortalView.as_view(), name="proposals_portal"),
    path("portal/analytics/", views.AnalyticsPortalView.as_view(), name="analytics_portal"),
    path("portal/community/", views.CommunityPortalView.as_view(), name="community_portal"),
    path("search/", views.SearchView.as_view(), name="search"),
]
