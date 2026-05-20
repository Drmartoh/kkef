"""Outbound mail helpers for public intake forms."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_donor_intake_notification(intake) -> bool:
    """Notify the donate inbox; attach file if present."""

    from apps.funding.models import DonorIntake

    if not isinstance(intake, DonorIntake):
        return False

    to = getattr(settings, "DONATE_INBOX_EMAIL", "donate@Kiambuempowermentforum.org")
    subject = f"[KKEF Donor] {intake.get_kind_display()} — {intake.reference}"
    lines = [
        f"Reference: {intake.reference}",
        f"Type: {intake.get_kind_display()}",
        f"Anonymous (public listing): {'Yes' if intake.anonymous else 'No'}",
        f"Name on file: {intake.display_name or '—'}",
        f"Email: {intake.email or '—'}",
        f"Phone: {intake.phone or '—'}",
        "",
    ]
    if intake.kind == DonorIntake.Kind.MONEY:
        lines.extend(
            [
                f"Amount: {intake.amount} {intake.currency}",
                f"Payment preference: {intake.payment_preference or '—'}",
            ]
        )
    elif intake.kind == DonorIntake.Kind.RESOURCES:
        cat = intake.get_resource_category_display() if intake.resource_category else "—"
        lines.extend(
            [
                f"Resource focus: {cat}",
                f"Details: {intake.resource_description or '—'}",
                f"Quantity / logistics: {intake.quantity_or_estimate or '—'}",
            ]
        )
    else:
        lines.extend(
            [
                f"Subject: {intake.message_subject or '—'}",
                f"Message:\n{intake.message_body or ''}",
            ]
        )

    body = "\n".join(lines)

    try:
        headers = {}
        if intake.email:
            headers["Reply-To"] = intake.email
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or "web@kkef.local",
            to=[to],
            headers=headers,
        )
        if intake.attachment:
            try:
                intake.attachment.open("rb")
                fname = intake.attachment.name.rsplit("/", 1)[-1]
                msg.attach(fname, intake.attachment.read())
            finally:
                intake.attachment.close()
        msg.send(fail_silently=False)
        intake.email_to_team_sent_at = timezone.now()
        intake.save(update_fields=["email_to_team_sent_at", "updated_at"])
        return True
    except Exception:
        logger.exception("Failed to send donor intake email for %s", intake.reference)
        return False


def send_group_application_notification(application) -> bool:
    from apps.organizations.models import GroupJoinApplication

    if not isinstance(application, GroupJoinApplication):
        return False

    to = getattr(settings, "DONATE_INBOX_EMAIL", "donate@Kiambuempowermentforum.org")
    subject = f"[KKEF Group application] {application.group_name} ({application.certificate_number})"
    body = "\n".join(
        [
            f"Certificate / registration no.: {application.certificate_number}",
            f"Group name: {application.group_name}",
            f"Ward: {application.get_ward_display()}",
            f"Group type: {application.get_group_type_display()}",
            f"Chairperson / contact: {application.chairperson_name}",
            f"Phone: {application.phone}",
            f"Contact email: {application.contact_email or '—'}",
            f"Status: {application.get_status_display()}",
        ]
    )
    try:
        headers = {}
        if application.contact_email:
            headers["Reply-To"] = application.contact_email
        EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or "web@kkef.local",
            to=[to],
            headers=headers,
        ).send(fail_silently=False)
        application.email_to_team_sent_at = timezone.now()
        application.save(update_fields=["email_to_team_sent_at", "updated_at"])
        return True
    except Exception:
        logger.exception("Failed to send group application email for %s", application.certificate_number)
        return False
