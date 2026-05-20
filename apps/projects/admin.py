from django.contrib import admin

from .models import KanbanLane, KanbanMembership, Project, ProjectMedia, ProjectMilestone, ProjectStakeholder


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0


class ProjectMediaInline(admin.TabularInline):
    model = ProjectMedia
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "status", "budget_total", "progress_percentage")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description", "location")
    autocomplete_fields = ("group", "steward")
    inlines = [ProjectMilestoneInline, ProjectMediaInline]


@admin.register(ProjectStakeholder)
class ProjectStakeholderAdmin(admin.ModelAdmin):
    autocomplete_fields = ("project", "stakeholder_user")


@admin.register(KanbanLane)
class KanbanLaneAdmin(admin.ModelAdmin):
    list_display = ("caption", "code")


@admin.register(KanbanMembership)
class KanbanMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "lane")
