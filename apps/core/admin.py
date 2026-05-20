from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "method", "path", "ip_address")
    list_filter = ("action", "method")
    search_fields = ("path",)
    readonly_fields = tuple(f.name for f in AuditLog._meta.fields)
