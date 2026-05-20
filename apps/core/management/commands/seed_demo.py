"""Populate the database with KKEF pilot content for previews and donor tours."""

from __future__ import annotations

from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.documents.models import Document
from apps.events.models import Event
from apps.funding.models import Donation, Sponsor
from apps.media_center.models import NewsArticle
from apps.organizations.models import CommunityGroup, GroupMembership
from apps.projects.models import Project, ProjectMilestone
from apps.proposals.models import Proposal


class Command(BaseCommand):
    help = "Seed illustrative groups, flagship projects, and governance artefacts."

    def handle(self, *args, **options):  # noqa: ARG002
        User = get_user_model()

        super_user, created = User.objects.get_or_create(
            username="kkef.super",
            defaults={
                "email": "ops@kkef.go.ke",
                "first_name": "Forum",
                "last_name": "Steward",
                "role": User.Roles.SUPER_ADMIN,
                "organization_title": "Forum Secretariat",
            },
        )
        if created:
            super_user.set_password("ChangeMe!2026")
            super_user.save()

        forum_admin, _ = User.objects.get_or_create(
            username="forum.admin",
            defaults={
                "email": "admin@kkef.go.ke",
                "role": User.Roles.FORUM_ADMIN,
            },
        )
        forum_admin.set_password("ForumAdmin!2026")
        forum_admin.save()

        leader, leader_created = User.objects.get_or_create(
            username="amaiagi.leader",
            defaults={
                "email": "leader@amaiagi.ke",
                "role": User.Roles.GROUP_LEADER,
            },
        )
        if leader_created:
            leader.set_password("LeaderDemo!2026")
            leader.save()

        stakeholder, _ = User.objects.get_or_create(
            username="county.partner",
            defaults={
                "email": "investor@government.go.ke",
                "role": User.Roles.STAKEHOLDER,
            },
        )
        stakeholder.set_password("StakeDemo!2026")
        stakeholder.save()

        donor, donor_created = User.objects.get_or_create(
            username="livingwaters.donor",
            defaults={
                "email": "giving@watershed.org",
                "role": User.Roles.DONOR,
            },
        )
        if donor_created:
            donor.set_password("DonorDemo!2026")
            donor.save()

        group_defs = [
            {
                "name": "Aminiagi Kambura CBO",
                "slug": slugify("Aminiagi Kambura CBO"),
                "group_type": CommunityGroup.GroupType.CBO,
                "summary": "Organic agriculture, gender finance circles, watershed dialogues.",
            },
            {
                "name": "Oasis Fish Farmers Group",
                "slug": slugify("Oasis Fish Farmers Group"),
                "group_type": CommunityGroup.GroupType.FISH_FARMERS,
                "summary": "Climate-smart aquaculture SACCO bridging extension and cold-chain mentors.",
            },
            {
                "name": "Karai Rising Youth Forum",
                "slug": slugify("Karai Rising Youth Forum"),
                "group_type": CommunityGroup.GroupType.YOUTH,
                "summary": "Green enterprise accelerators anchored in mentorship and civic-tech labs.",
            },
        ]

        groups = []
        for payload in group_defs:
            data = payload.copy()
            slug = data.pop("slug")
            grp, _ = CommunityGroup.objects.get_or_create(slug=slug, defaults=data)
            grp.is_published = True
            grp.is_featured = True
            grp.members_count_cached = {
                slugify("Aminiagi Kambura CBO"): 182,
                slugify("Oasis Fish Farmers Group"): 96,
                slugify("Karai Rising Youth Forum"): 240,
            }.get(grp.slug, 120)
            grp.latitude = grp.latitude or Decimal("-1.1733")
            grp.longitude = grp.longitude or Decimal("36.9376")
            grp.save()
            groups.append(grp)

        if groups:
            groups[0].leaders.add(leader)
            GroupMembership.objects.get_or_create(user=leader, group=groups[0])
            GroupMembership.objects.get_or_create(user=leader, group=groups[1])

        project_specs = [
            {
                "title": "Integrated Bio-Enterprise Corridors",
                "budget": Decimal("8450000"),
                "status": Project.Status.ONGOING,
                "progress": 64,
                "tags": "tree,soil-health,youth,green-jobs",
            },
            {
                "title": "Aquaculture Cold-Chain Stewardship Pilot",
                "budget": Decimal("5620000"),
                "status": Project.Status.APPROVED,
                "progress": 32,
                "tags": "aquaculture,innovation,market-access",
            },
            {
                "title": "Countywide Clean-Up Observatory",
                "budget": Decimal("2150000"),
                "status": Project.Status.APPROVED,
                "progress": 48,
                "tags": "cleanup,circular,waste-mapping",
            },
        ]

        for idx, payload in enumerate(project_specs):
            target_group = groups[idx % len(groups)]
            slug = slugify(payload["title"])
            project, _ = Project.objects.get_or_create(
                slug=slug,
                defaults={
                    "group": target_group,
                    "title": payload["title"],
                    "description": "Co-designed with wards, SACCO councils, environmental stewards.",
                    "budget_total": payload["budget"],
                    "status": payload["status"],
                    "timeline_start": timezone.now().date() - timedelta(days=120),
                    "timeline_end": timezone.now().date() + timedelta(days=620),
                    "location": "Karai / Ting'ang'a wards",
                    "latitude": Decimal("-1.1733"),
                    "longitude": Decimal("36.9376"),
                    "beneficiaries_count": [4200, 3100, 8900][idx],
                    "sdg_goals": [["2", "5", "13"], ["13", "14"], ["11", "12"]][idx],
                    "intervention_tags": payload["tags"],
                    "progress_percentage": payload["progress"],
                    "steward": leader,
                    "reference_code": f"PR-{idx+1}-{timezone.now().year}",
                },
            )
            milestones = [
                ("Community baselines synced", timezone.now().date(), timezone.now().date()),
                ("Extension kits released", timezone.now().date(), timezone.now().date()),
                ("Monitoring dashboards calibrated", timezone.now().date(), None),
            ]
            for ordering, trio in enumerate(milestones):
                ProjectMilestone.objects.get_or_create(
                    project=project,
                    title=trio[0],
                    defaults={
                        "baseline_date": trio[1],
                        "target_date": trio[2],
                        "sort_order": ordering,
                    },
                )

        Proposal.objects.get_or_create(
            slug=slugify("Smart Watershed Co-Investment"),
            defaults={
                "reference": "KP-9981",
                "owning_group": groups[0],
                "authored_by": leader,
                "title": "Smart Watershed Co-Investment Facility",
                "category": Proposal.Category.WATER,
                "synopsis": "Climate-smart micro-dams anchored in youth-led GIS monitoring.",
                "implementation_plan": "Phase 1: hydrology sensors. Phase 2: blended grants + county loan guarantees.",  # noqa: E501
                "projected_budget": Decimal("12250000"),
                "status": Proposal.Status.UNDER_REVIEW,
                "beneficiaries_estimate": 12400,
            },
        )

        sponsor, _ = Sponsor.objects.get_or_create(
            slug=slugify("Rivertree Giving Circle"),
            defaults={
                "name": "Rivertree Giving Circle",
                "tier": "Platinum",
                "headline": "Supporting transparent youth aquaculture modernization.",
                "liaison_user": donor,
            },
        )

        Donation.objects.get_or_create(
            reference="DEMO-ALPHA",
            defaults={
                "donor": donor,
                "sponsor": sponsor,
                "currency": "KES",
                "amount": Decimal("350000"),
                "channel": Donation.Channel.CARD,
                "status": Donation.Status.COMPLETED,
                "earmark_category": "youth-enterprise",
                "donor_display_name": "Riverlight Foundation",
            },
        )

        Event.objects.get_or_create(
            slug=slugify("Karai Habitat Restoration Mobilization"),
            defaults={
                "title": "Karai Habitat Restoration Mobilization",
                "start_at": timezone.now() + timedelta(days=21),
                "end_at": timezone.now() + timedelta(days=21, hours=4),
                "venue_descriptor": "Ridgeview Social Hall + riparian buffer",
                "summary": "Tree equity mapping, SACCO underwriting clinics, participatory GIS mapping.",
                "stewardship_lead": forum_admin,
                "organizer_group": groups[2],
                "latitude": Decimal("-1.1744"),
                "longitude": Decimal("36.9411"),
                "ticketing_fee": Decimal("350"),
                "ticketing_currency": "KES",
                "ticketing_enabled": True,
                "capacity": 400,
            },
        )

        charter_slug = slugify("2025 Transparency Charter")
        charter, created = Document.objects.get_or_create(
            slug=charter_slug,
            defaults={
                "title": "2025 Transparency Charter — Digital Edition",
                "doc_type": Document.DocType.POLICY,
                "visibility": Document.Visibility.PUBLIC,
                "uploaded_by": forum_admin,
            },
        )
        if created or not charter.file.name:
            payload = ContentFile(
                b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\nHello KKEF\n",
                name="2025-charter-demo.pdf",
            )
            charter.file.save(payload.name, payload, save=True)

        NewsArticle.objects.get_or_create(
            slug=slugify("County Stakeholders Co-Design Transparency Stack"),
            defaults={
                "title": "County Stakeholders Co-Design Transparency Stack",
                "status": NewsArticle.Status.PUBLISHED,
                "summary": "GIS-rich dashboards unify ward-level giving, SACCO liquidity, ecological gains.",
                "body": "<p>Ward champions and donor partners convened in Karai...</p>",
                "authored_by": forum_admin,
                "spotlight_quote": "Our youth now trace every disbursement visually — not just academically.",
                "tags_csv": "Governance,Giving,Climate",
            },
        )

        self.stdout.write(self.style.SUCCESS("KKEF preview dataset seeded with county-grade storytelling artefacts."))
