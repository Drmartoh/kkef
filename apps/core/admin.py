from django.contrib import admin
from django.utils.html import format_html

from .models import AuditLog, ForumOfficial


@admin.register(ForumOfficial)
class ForumOfficialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "tier", "is_published", "sort_order", "portrait_preview")
    list_editable = ("sort_order", "is_published")
    list_filter = ("tier", "is_published")
    search_fields = ("name", "role", "tagline")
    ordering = ("tier", "sort_order", "name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "tier",
                    "name",
                    "role",
                    "tagline",
                    "photo",
                    "portrait_preview",
                    "is_published",
                    "sort_order",
                )
            },
        ),
        ("Profile", {"fields": ("bio", "tenure", "focus_areas")}),
    )
    readonly_fields = ("portrait_preview",)

    @admin.display(description="Photo")
    def portrait_preview(self, obj: ForumOfficial) -> str:
        if not obj.pk:
            return "—"
        url = obj.photo_url
        return format_html(
            '<img src="{}" alt="" style="height:96px;width:96px;border-radius:9999px;object-fit:cover;" />',
            url,
        )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "method", "path", "ip_address")
    list_filter = ("action", "method")
    search_fields = ("path",)
    readonly_fields = tuple(f.name for f in AuditLog._meta.fields)
