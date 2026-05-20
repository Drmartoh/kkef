"""
URL routing for KKEF: public templates, dashboards, Django admin, API v1, integrations.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from apps.integrations import views as integrations_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("api/auth/", include("apps.accounts.auth_urls")),
    path("api/v1/", include("apps.integrations.api_urls")),
    path("payments/stripe/webhook/", integrations_views.stripe_webhook),
    path("payments/mpesa/callback/", integrations_views.mpesa_callback_stub),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path("api/schema/", TemplateView.as_view(template_name="api_placeholder.html")),
    ]

admin.site.site_header = "KKEF Administration"
admin.site.site_title = "KKEF Admin"
admin.site.index_title = "Forum operations"
