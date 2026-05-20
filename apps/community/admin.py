from django.contrib import admin

from apps.community import models


@admin.register(models.Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ("name", "moderated")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.DiscussionThread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "forum", "pinned", "updated_at")


@admin.register(models.DiscussionPost)
class PostAdmin(admin.ModelAdmin):
    search_fields = ("body",)


@admin.register(models.Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("question",)


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(models.FeedbackSubmission)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("category", "created_at")
