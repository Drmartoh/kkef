"""
Leadership seed data and helpers for the public Officials page.
"""

from urllib.parse import quote_plus

from apps.core.models import ForumOfficial


def placeholder_avatar(name: str, bg: str = "0f172a", fg: str = "ffffff") -> str:
    return (
        "https://ui-avatars.com/api/"
        f"?name={quote_plus(name)}&size=512&background={bg}&color={fg}"
        "&bold=true&format=png"
    )


def _exec(
    order: int,
    name: str,
    role: str,
    tagline: str,
    bio: str,
    tenure: str,
    focus: list[str],
) -> dict:
    return {
        "tier": ForumOfficial.Tier.EXECUTIVE,
        "sort_order": order,
        "name": name,
        "role": role,
        "tagline": tagline,
        "bio": bio,
        "tenure": tenure,
        "focus_areas": focus,
    }


def _ext(
    order: int,
    name: str,
    role: str,
    tagline: str,
    bio: str,
    tenure: str,
    focus: list[str],
) -> dict:
    return {
        "tier": ForumOfficial.Tier.EXTENDED,
        "sort_order": order,
        "name": name,
        "role": role,
        "tagline": tagline,
        "bio": bio,
        "tenure": tenure,
        "focus_areas": focus,
    }


DEFAULT_OFFICIALS = [
    _exec(
        1,
        "Jackson Kamau",
        "Chairperson",
        "Stewardship & county alignment",
        (
            "Jackson provides strategic direction for KKEF, anchoring ward priorities "
            "with county development plans and safeguarding fiduciary discipline across "
            "all community programmes."
        ),
        "Serving since forum incorporation",
        ["Board governance", "County partnerships", "Strategic planning"],
    ),
    _exec(
        2,
        "Geoffrey Mwangi",
        "Vice Chairperson",
        "Operations & member cohesion",
        (
            "Geoffrey coordinates executive sessions, mentors group leaders, and ensures "
            "SACCO and CBO clusters receive timely guidance on compliance and reporting."
        ),
        "Executive board",
        ["Member onboarding", "SACCO liaison", "Conflict resolution"],
    ),
    _exec(
        3,
        "Grace Wanjiru Njeri",
        "Secretary",
        "Records, minutes & correspondence",
        (
            "Grace maintains the forum register, circulates board resolutions, and keeps "
            "archival minutes accessible to members and county oversight teams."
        ),
        "Executive board",
        ["Board papers", "Member registry", "Compliance filings"],
    ),
    _exec(
        4,
        "Peter Ndung'u Kariuki",
        "Treasurer",
        "Finance, audits & transparent giving",
        (
            "Peter oversees budgets, donation reconciliation, and quarterly transparency "
            "reports published on the KKEF impact dashboard."
        ),
        "Executive board",
        ["Treasury controls", "Donor reporting", "Grant disbursement"],
    ),
    _exec(
        5,
        "Mary Nyokabi Chege",
        "Committee Member",
        "Programmes & field verification",
        (
            "Mary chairs the programmes committee, verifying milestone evidence from "
            "ward projects before funds are released to implementing groups."
        ),
        "Elected committee",
        ["Project verification", "Ward visits", "Safeguarding"],
    ),
    _ext(
        1,
        "Rev. Samuel Githinji",
        "Patron & Moral Trustee",
        "Ethics & community witness",
        (
            "Provides pastoral oversight and witnesses public accountability forums "
            "between KKEF, faith communities, and elders' councils."
        ),
        "Honorary patron",
        ["Ethics charter", "Peace building", "Interfaith dialogue"],
    ),
    _ext(
        2,
        "Faith Muthoni Karimi",
        "Women & Gender Lead",
        "Inclusion & livelihoods",
        (
            "Champions women's table banking clusters, gender-responsive budgeting, "
            "and safe spaces for survivors of gender-based violence."
        ),
        "Standing committee",
        ["Women's SACCOs", "GBV referrals", "Skills training"],
    ),
    _ext(
        3,
        "Brian Kariuki Waweru",
        "Youth Representative",
        "Innovation & digital inclusion",
        (
            "Mobilises youth agripreneurs and green-tech pilots, bridging KKEF "
            "dashboards with campus and innovation hub partners."
        ),
        "Youth caucus",
        ["Green jobs", "Mentorship", "Hackathons"],
    ),
    _ext(
        4,
        "Diana Wambui Muturi",
        "Communications Officer",
        "Media, branding & public engagement",
        (
            "Curates press releases, social campaigns, and crisis communications "
            "so every ward hears verified KKEF updates."
        ),
        "Secretariat",
        ["Media bureau", "Community radio", "Crisis comms"],
    ),
    _ext(
        5,
        "James Otieno Oduor",
        "Programmes Coordinator",
        "Delivery & GIS intelligence",
        (
            "Synchronises project kanban boards, GIS layers, and donor milestone "
            "reports across Karai wards and neighbouring clusters."
        ),
        "Secretariat",
        ["GIS maps", "M&E", "Partner MOUs"],
    ),
    _ext(
        6,
        "Adv. Lucy Njeri Kamau",
        "Legal Advisor",
        "Governance & agreements",
        (
            "Reviews constitutions, MOUs, and procurement frameworks to keep KKEF "
            "aligned with Kenyan NGO and county partnership law."
        ),
        "Advisory",
        ["Contracts", "Policy drafts", "Dispute mediation"],
    ),
]


def seed_officials() -> int:
    """Create default officials when the table is empty."""
    if ForumOfficial.objects.exists():
        return 0
    ForumOfficial.objects.bulk_create([ForumOfficial(**row) for row in DEFAULT_OFFICIALS])
    return len(DEFAULT_OFFICIALS)


def get_officials_context() -> dict:
    seed_officials()
    published = ForumOfficial.objects.filter(is_published=True)
    return {
        "executive_officials": published.filter(tier=ForumOfficial.Tier.EXECUTIVE),
        "extended_officials": published.filter(tier=ForumOfficial.Tier.EXTENDED),
    }
