from django.contrib import admin

from .models import Donation, DonorIntake, Sponsor


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "is_active")
    search_fields = ("name", "slug", "headline")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("liaison_user",)


@admin.register(DonorIntake)
class DonorIntakeAdmin(admin.ModelAdmin):
    list_display = ("reference", "kind", "display_name", "email", "anonymous", "created_at")
    list_filter = ("kind", "anonymous")
    search_fields = ("reference", "email", "display_name", "message_body")
    readonly_fields = ("reference", "email_to_team_sent_at", "created_at", "updated_at")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("reference", "amount", "channel", "status", "donor", "created_at")
    list_filter = ("status", "channel")
    autocomplete_fields = ("donor", "project", "sponsor")
    readonly_fields = ("created_at", "updated_at")
