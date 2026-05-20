"""Lightweight HTTP activity logging."""

from django.utils.deprecation import MiddlewareMixin


class ActivityAuditMiddleware(MiddlewareMixin):
    """
    Writes high-level access records for authenticated dashboard/API users.
    Skips static/media to reduce noise.
    """

    SKIP_PREFIXES = ("/static/", "/media/", "/favicon.ico")

    def process_response(self, request, response):
        path = getattr(request, "path", "") or ""
        if any(path.startswith(p) for p in self.SKIP_PREFIXES):
            return response
        user = getattr(request, "user", None)
        if user and user.is_authenticated and request.method != "GET":
            from apps.core.models import AuditLog

            AuditLog.objects.create(
                user=user,
                action="http_request",
                path=path[:512],
                method=request.method[:8],
                ip_address=_client_ip(request),
                metadata={
                    "status_code": getattr(response, "status_code", None),
                },
            )
        return response


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
