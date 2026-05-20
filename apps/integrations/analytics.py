"""Cross-cutting KPI builders used by dashboards and public transparency tiles."""

from __future__ import annotations

from django.db.models import Count, Sum

from apps.events.models import Event
from apps.funding.models import Donation
from apps.organizations.models import CommunityGroup
from apps.projects.models import Project
from apps.proposals.models import Proposal


def public_transparency_cards() -> dict:
    grouped_cbos = CommunityGroup.objects.filter(is_published=True).count()
    thriving_projects = Project.objects.filter(status__in=["approved", "ongoing", "completed"]).count()
    disbursements = Donation.objects.filter(status=Donation.Status.COMPLETED).aggregate(
        tally=Sum("amount")
    )["tally"] or 0
    stewardship_queue = Proposal.objects.filter(
        status__in=[Proposal.Status.UNDER_REVIEW, Proposal.Status.AWAITING_APPROVAL]
    ).count()
    stewardship_events = Event.objects.upcoming().filter(is_public=True).count()

    return {
        "grouped_cbos": grouped_cbos,
        "portfolio_projects": thriving_projects,
        "verified_giving_kes": float(disbursements),
        "governance_queues": stewardship_queue + stewardship_events,
    }


def executive_pulse() -> dict:
    snapshots = Project.objects.values("status").annotate(total=Count("id"))
    thematic_intensity = (
        Project.objects.values("group__group_type").annotate(weight=Sum("budget_total")).order_by("-weight")[
            :5
        ]
    )
    runway = Proposal.objects.order_by("-projected_budget")[:5].values(
        "title",
        "projected_budget",
        "status",
        "reference",
    )
    sponsorship_matrix = CommunityGroup.objects.annotate(volume=Sum("projects__budget_total")).order_by("-volume")[
        :8
    ]

    payload = public_transparency_cards()
    payload.update(
        {
            "status_breakdown": list(snapshots),
            "capital_by_constituency": list(thematic_intensity),
            "pipeline_watchlist": list(runway),
            "capital_by_group": [
                {
                    "group": grp.name or str(grp.pk),
                    "volume": float(grp.volume or 0),
                }
                for grp in sponsorship_matrix
            ],
        }
    )

    return payload
