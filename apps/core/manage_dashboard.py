"""
Data builders for the interactive management control center.
"""

from __future__ import annotations

from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import AuditLog, ForumOfficial
from apps.documents.models import Document
from apps.events.models import Event
from apps.funding.models import Donation, DonorIntake
from apps.integrations.analytics import executive_pulse, public_transparency_cards
from apps.media_center.models import NewsArticle
from apps.organizations.models import CommunityGroup, GroupJoinApplication
from apps.projects.models import Project
from apps.proposals.models import Proposal


def manage_nav_sections() -> list[dict]:
    """Sidebar modules for the in-dashboard workspace (no Django admin required)."""
    return [
        {"title": "Overview", "icon": "fa-gauge-high", "module": "overview"},
        {"title": "Projects", "icon": "fa-diagram-project", "module": "projects"},
        {"title": "Officials", "icon": "fa-user-tie", "module": "officials"},
        {"title": "Groups", "icon": "fa-people-group", "module": "groups"},
        {"title": "Events", "icon": "fa-calendar-days", "module": "events"},
        {"title": "News", "icon": "fa-newspaper", "module": "news"},
        {"title": "Proposals", "icon": "fa-file-lines", "module": "proposals"},
        {"title": "Documents", "icon": "fa-folder-open", "module": "documents"},
        {"title": "Donor inbox", "icon": "fa-hand-holding-heart", "module": "donor_intakes"},
        {"title": "Group applications", "icon": "fa-building-circle-check", "module": "group_applications"},
        {"title": "Donations", "icon": "fa-coins", "module": "donations"},
        {"title": "Users", "icon": "fa-users-gear", "module": "users"},
    ]


def _action_queue() -> list[dict]:
    items: list[dict] = []

    for app in GroupJoinApplication.objects.filter(
        status__in=[GroupJoinApplication.Status.PENDING, GroupJoinApplication.Status.UNDER_REVIEW]
    ).order_by("-created_at")[:8]:
        items.append(
            {
                "kind": "group_application",
                "label": "Group application",
                "title": app.group_name,
                "meta": f"{app.get_status_display()} · {app.ward}",
                "when": app.created_at.isoformat(),
                "module": "group_applications",
                "id": app.certificate_number,
            }
        )

    for proposal in Proposal.objects.filter(
        status__in=[Proposal.Status.UNDER_REVIEW, Proposal.Status.AWAITING_APPROVAL, Proposal.Status.SUBMITTED]
    ).order_by("-updated_at")[:8]:
        items.append(
            {
                "kind": "proposal",
                "label": "Proposal",
                "title": proposal.title,
                "meta": proposal.get_status_display(),
                "when": proposal.updated_at.isoformat(),
                "module": "proposals",
                "id": str(proposal.pk),
            }
        )

    for project in Project.objects.filter(
        status__in=[Project.Status.PENDING, Project.Status.UNDER_REVIEW]
    ).order_by("-updated_at")[:8]:
        items.append(
            {
                "kind": "project",
                "label": "Project",
                "title": project.title,
                "meta": project.get_status_display(),
                "when": project.updated_at.isoformat(),
                "module": "projects",
                "id": str(project.pk),
            }
        )

    for intake in DonorIntake.objects.order_by("-created_at")[:6]:
        items.append(
            {
                "kind": "donor_intake",
                "label": "Donor submission",
                "title": intake.display_name or intake.reference,
                "meta": intake.get_kind_display(),
                "when": intake.created_at.isoformat(),
                "module": "donor_intakes",
                "id": str(intake.pk),
            }
        )

    for donation in Donation.objects.filter(status=Donation.Status.PENDING).order_by("-created_at")[:6]:
        items.append(
            {
                "kind": "donation",
                "label": "Pending donation",
                "title": str(donation.reference or donation.pk),
                "meta": f"{donation.amount} {donation.currency}",
                "when": donation.created_at.isoformat(),
                "module": "donations",
                "id": str(donation.pk),
            }
        )

    items.sort(key=lambda row: row["when"], reverse=True)
    return items[:20]


def build_manage_snapshot() -> dict:
    tiles = public_transparency_cards()
    pulse = executive_pulse()

    pending_groups = GroupJoinApplication.objects.filter(
        status__in=[GroupJoinApplication.Status.PENDING, GroupJoinApplication.Status.UNDER_REVIEW]
    ).count()
    pending_proposals = Proposal.objects.filter(
        status__in=[
            Proposal.Status.SUBMITTED,
            Proposal.Status.UNDER_REVIEW,
            Proposal.Status.AWAITING_APPROVAL,
        ]
    ).count()
    pending_projects = Project.objects.filter(
        status__in=[Project.Status.PENDING, Project.Status.UNDER_REVIEW]
    ).count()
    new_donor_intakes = DonorIntake.objects.count()
    pending_donations = Donation.objects.filter(status=Donation.Status.PENDING).count()
    officials_published = ForumOfficial.objects.filter(is_published=True).count()
    draft_articles = NewsArticle.objects.exclude(status=NewsArticle.Status.PUBLISHED).count()
    upcoming_events = Event.objects.upcoming().count()
    active_users = User.objects.filter(is_active=True).count()

    from collections import defaultdict

    monthly: dict[str, float] = defaultdict(float)
    for row in Donation.objects.filter(status=Donation.Status.COMPLETED).values("created_at", "amount"):
        key = row["created_at"].strftime("%Y-%m")
        monthly[key] += float(row["amount"] or 0)
    donation_trend = [
        {"month": month, "total": round(total, 2)}
        for month, total in sorted(monthly.items())[-6:]
    ]

    return {
        "generated_at": timezone.now().isoformat(),
        "kpis": {
            "published_groups": tiles["grouped_cbos"],
            "active_projects": tiles["portfolio_projects"],
            "verified_giving_kes": tiles["verified_giving_kes"],
            "governance_queue": tiles["governance_queues"],
            "pending_groups": pending_groups,
            "pending_proposals": pending_proposals,
            "pending_projects": pending_projects,
            "donor_intakes": new_donor_intakes,
            "pending_donations": pending_donations,
            "officials_live": officials_published,
            "draft_articles": draft_articles,
            "upcoming_events": upcoming_events,
            "active_users": active_users,
            "inbox_total": pending_groups
            + pending_proposals
            + pending_projects
            + pending_donations,
        },
        "charts": {
            "project_status": pulse.get("status_breakdown", []),
            "donation_trend": donation_trend,
            "queue_breakdown": [
                {"label": "Group applications", "total": pending_groups},
                {"label": "Proposals", "total": pending_proposals},
                {"label": "Projects", "total": pending_projects},
                {"label": "Donations", "total": pending_donations},
            ],
        },
        "action_queue": _action_queue(),
        "recent_audit": [
            {
                "action": entry.action,
                "path": entry.path,
                "user": entry.user.username if entry.user_id else "system",
                "when": entry.created_at.isoformat(),
            }
            for entry in AuditLog.objects.select_related("user").order_by("-created_at")[:12]
        ],
        "quick_counts": {
            "officials": ForumOfficial.objects.count(),
            "groups": CommunityGroup.objects.count(),
            "projects": Project.objects.count(),
            "proposals": Proposal.objects.count(),
            "events": Event.objects.count(),
            "articles": NewsArticle.objects.count(),
            "documents": Document.objects.count(),
        },
    }


def build_manage_context() -> dict:
    snapshot = build_manage_snapshot()
    return {
        "manage_nav": manage_nav_sections(),
        "manage_snapshot": snapshot,
    }
