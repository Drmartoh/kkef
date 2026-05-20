from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "doc_type", "visibility", "version_label", "created_at")
    search_fields = ("title",)
    autocomplete_fields = ("group", "project", "proposal", "uploaded_by")
