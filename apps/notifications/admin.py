from django.contrib import admin

from .models import Notification, OutreachTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "channel", "read_at", "created_at")
    search_fields = ("title",)


@admin.register(OutreachTemplate)
class OutreachTemplateAdmin(admin.ModelAdmin):
    search_fields = ("key",)
