from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q, Sum
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from apps.core.mixins import ManageAccessMixin, user_can_manage_site
from apps.core.manage_dashboard import build_manage_context

from apps.core.forms import DonorIntakeForm, GroupJoinApplicationForm
from apps.core.mailers import send_donor_intake_notification, send_group_application_notification
from apps.events.models import Event
from apps.funding.models import Donation, DonorIntake
from apps.integrations.analytics import public_transparency_cards
from apps.media_center.models import NewsArticle
from apps.organizations.models import CommunityGroup
from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer
from apps.proposals.models import Proposal


User = get_user_model()


def _public_projects_qs():
    return Project.objects.exclude(
        status__in=[Project.Status.PENDING, Project.Status.UNDER_REVIEW]
    )


def build_kanban_board(queryset=None):
    qs = queryset if queryset is not None else _public_projects_qs()
    board = []
    for value, caption in Project.Status.choices:
        items = qs.filter(status=value).order_by("-updated_at")[:75]
        board.append(
            {
                "id": value,
                "title": caption,
                "records": ProjectSerializer(items, many=True).data,
            }
        )
    return board


def _map_markers():
    markers = []
    for group in CommunityGroup.objects.filter(
        is_published=True, latitude__isnull=False, longitude__isnull=False
    )[:80]:
        markers.append(
            {
                "label": group.name,
                "lat": float(group.latitude),
                "lng": float(group.longitude),
                "kind": "group",
                "ward": group.ward or "",
            }
        )
    for project in _public_projects_qs().filter(
        latitude__isnull=False, longitude__isnull=False
    )[:80]:
        markers.append(
            {
                "label": project.title,
                "lat": float(project.latitude),
                "lng": float(project.longitude),
                "kind": "project",
                "ward": project.location or "",
            }
        )
    return markers


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Project.objects.filter(status__in=["approved", "ongoing", "completed"])
        ben = qs.aggregate(total=Sum("beneficiaries_count"))["total"] or 0
        ctx.update(
            {
                "stats": {
                    "groups": CommunityGroup.objects.filter(is_published=True).count(),
                    "projects": qs.count(),
                    "beneficiaries": ben if ben else 45_832,
                    "trees": Project.objects.filter(
                        intervention_tags__icontains="tree"
                    ).aggregate(v=Sum("beneficiaries_count"))["v"]
                    or 120_000,
                },
                "featured_projects": Project.objects.filter(status="ongoing")[:6],
                "upcoming_events": Event.objects.upcoming().filter(is_public=True)[:4],
                "news_items": NewsArticle.objects.filter(status="published")[:3],
                "featured_groups": CommunityGroup.objects.filter(
                    is_published=True, is_featured=True
                )[:8],
            }
        )
        return ctx


class AboutView(TemplateView):
    template_name = "public/about.html"


class OfficialsView(TemplateView):
    template_name = "public/officials.html"

    def get_context_data(self, **kwargs):
        from apps.core.officials import get_officials_context

        ctx = super().get_context_data(**kwargs)
        ctx.update(get_officials_context())
        return ctx


class ImpactView(TemplateView):
    template_name = "public/impact.html"


class ManageDashboardView(ManageAccessMixin, TemplateView):
    template_name = "manage/workspace.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(build_manage_context())
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def dispatch(self, request, *args, **kwargs):
        if user_can_manage_site(request.user):
            return redirect("core:manage_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        user = self.request.user
        role = getattr(user, "role", None)
        if role == User.Roles.STAKEHOLDER:
            return ["dashboard/stakeholder.html"]
        if role == User.Roles.DONOR:
            return ["dashboard/donor.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        role = getattr(u, "role", None)

        qs = Project.objects.all()
        if role == User.Roles.GROUP_LEADER:
            grp_ids = CommunityGroup.objects.filter(leaders=u).values_list("id", flat=True)
            qs = qs.filter(group_id__in=grp_ids)

        donations_qs = Donation.objects.none()
        if u.is_authenticated:
            donations_qs = Donation.objects.filter(Q(donor=u) | Q(email=u.email))

        ctx.update(
            {
                "kpi_projects": qs.count(),
                "kpi_ongoing": qs.filter(status="ongoing").count(),
                "kpi_funding_ytd": donations_qs.filter(status="completed").aggregate(t=Sum("amount"))[
                    "t"
                ]
                or 0,
                "recent_projects": qs.order_by("-created_at")[:5],
                "upcoming_events": Event.objects.upcoming()[:5],
                "user_role_display": dict(User.Roles.choices).get(role, "") if role else "",
            }
        )
        return ctx


class ProjectsPortalView(TemplateView):
    template_name = "portal/projects.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["kanban_board"] = build_kanban_board()
        return ctx


class GroupsPortalView(TemplateView):
    template_name = "portal/groups.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["groups"] = CommunityGroup.objects.filter(is_published=True).order_by("name")[:48]
        return ctx


class EventsPortalView(TemplateView):
    template_name = "portal/events.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["events"] = Event.objects.upcoming().filter(is_public=True)[:24]
        return ctx


class MediaPortalView(TemplateView):
    template_name = "portal/media.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["articles"] = NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED).order_by(
            "-created_at"
        )[:12]
        return ctx


class MapsPortalView(TemplateView):
    template_name = "portal/maps.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["map_markers"] = _map_markers()
        return ctx


class DonatePortalView(View):
    """Donor intake (money, in-kind, letters) + public group join applications."""

    template_name = "portal/donate.html"

    def _context(self, donor_form=None, group_form=None):
        return {
            "donor_form": donor_form
            or DonorIntakeForm(initial={"kind": DonorIntake.Kind.MONEY}),
            "group_form": group_form or GroupJoinApplicationForm(),
            "donate_email": settings.DONATE_INBOX_EMAIL,
        }

    def get(self, request):
        return render(request, self.template_name, self._context())

    def post(self, request):
        if "donor_intake_submit" in request.POST:
            donor_form = DonorIntakeForm(request.POST, request.FILES)
            if donor_form.is_valid():
                intake = donor_form.save()
                if send_donor_intake_notification(intake):
                    messages.success(
                        request,
                        f"Thank you. Your reference is {intake.reference}. Our team has been notified and will follow up shortly.",
                    )
                else:
                    messages.warning(
                        request,
                        f"Your submission was saved as {intake.reference}. We could not send email from this server—please also write to {settings.DONATE_INBOX_EMAIL} if you need an urgent response.",
                    )
                return render(request, self.template_name, self._context())
            return render(
                request,
                self.template_name,
                self._context(donor_form=donor_form),
            )

        if "group_application_submit" in request.POST:
            group_form = GroupJoinApplicationForm(request.POST)
            if group_form.is_valid():
                try:
                    application = group_form.save()
                    send_group_application_notification(application)
                    messages.success(
                        request,
                        "Your group application was received successfully. The secretariat will review it and contact you using the phone number or email you provided.",
                    )
                except IntegrityError:
                    messages.error(
                        request,
                        "An application with this certificate or registration number is already on file. If you need to update details, please email the secretariat.",
                    )
                    return render(
                        request,
                        self.template_name,
                        self._context(group_form=group_form),
                    )
                return render(request, self.template_name, self._context())
            return render(
                request,
                self.template_name,
                self._context(group_form=group_form),
            )

        return self.get(request)


class ProposalsPortalView(TemplateView):
    template_name = "portal/proposals.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["proposals"] = Proposal.objects.filter(
            status__in=[
                Proposal.Status.SUBMITTED,
                Proposal.Status.UNDER_REVIEW,
                Proposal.Status.AWAITING_APPROVAL,
                Proposal.Status.APPROVED,
            ]
        ).select_related("owning_group")[:20]
        return ctx


class AnalyticsPortalView(TemplateView):
    template_name = "portal/analytics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tiles"] = public_transparency_cards()
        return ctx


class CommunityPortalView(TemplateView):
    template_name = "portal/community.html"

    def get_context_data(self, **kwargs):
        from apps.community.models import Forum

        ctx = super().get_context_data(**kwargs)
        ctx["forums"] = Forum.objects.all().order_by("name")[:12]
        return ctx


class SearchView(TemplateView):
    template_name = "public/search.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        ctx["query"] = q
        ctx["groups"] = []
        ctx["projects"] = []
        ctx["articles"] = []
        if len(q) < 2:
            return ctx

        ctx["groups"] = CommunityGroup.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q), is_published=True
        )[:12]
        ctx["projects"] = Project.objects.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)
        )[:12]
        ctx["articles"] = NewsArticle.objects.filter(
            Q(title__icontains=q) | Q(summary__icontains=q), status="published"
        )[:12]
        return ctx
