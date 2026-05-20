from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserActivity


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "role", "phone", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    ordering = ("username",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("KKEF profile", {"fields": ("role", "phone", "avatar", "organization_title", "prefers_dark_mode", "two_factor_enabled")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("KKEF profile", {"fields": ("role", "phone")}),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "target_model", "target_id")
    readonly_fields = tuple(f.name for f in UserActivity._meta.fields)
