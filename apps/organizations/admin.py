from django.contrib import admin

from .models import CommunityGroup, GroupJoinApplication, GroupMembership


@admin.register(GroupJoinApplication)
class GroupJoinApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "certificate_number",
        "group_name",
        "ward_label",
        "group_type",
        "chairperson_name",
        "phone",
        "status",
        "created_at",
    )

    @admin.display(description="Ward")
    def ward_label(self, obj):
        return obj.get_ward_display()
    list_filter = ("status", "group_type", "ward")
    search_fields = ("group_name", "certificate_number", "chairperson_name", "phone")
    readonly_fields = ("email_to_team_sent_at", "created_at", "updated_at")


@admin.register(CommunityGroup)
class CommunityGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "group_type", "county", "is_published", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "registration_number")
    filter_horizontal = ("leaders",)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "role", "verified")
    autocomplete_fields = ("user", "group")
