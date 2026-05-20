from django.conf import settings

from apps.core.contacts import get_contact_phones


def branding(_request):
    return {
        "PUBLIC_SITE_URL": settings.PUBLIC_SITE_URL,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        "LEAFLET_TILE_URL": settings.LEAFLET_TILE_URL,
        "DONATE_INBOX_EMAIL": getattr(settings, "DONATE_INBOX_EMAIL", "donate@Kiambuempowermentforum.org"),
    }


def site_contacts(_request):
    return {"KKEF_PHONES": get_contact_phones()}
