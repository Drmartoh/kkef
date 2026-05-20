"""Site-wide contact details exposed to templates."""

from django.conf import settings


def _to_tel(display: str) -> str:
    digits = "".join(ch for ch in display if ch.isdigit())
    if digits.startswith("254"):
        return f"+{digits}"
    if digits.startswith("0") and len(digits) >= 9:
        return f"+254{digits[1:]}"
    if digits:
        return f"+{digits}"
    return ""


def get_contact_phones() -> list[dict[str, str]]:
    raw = getattr(settings, "KKEF_CONTACT_PHONES", ["0720 463 430", "0726 622 206"])
    phones = []
    for item in raw:
        display = str(item).strip()
        if not display:
            continue
        phones.append({"display": display, "tel": _to_tel(display)})
    return phones
