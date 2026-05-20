from django.contrib import admin

from .models import Proposal, ProposalAttachment, ProposalDigitalSignature, ProposalReview


class AttachmentInline(admin.TabularInline):
    model = ProposalAttachment
    extra = 0


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "owning_group", "authored_by")
    list_filter = ("status", "category")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "synopsis")
    autocomplete_fields = ("owning_group", "authored_by")
    inlines = [AttachmentInline]


@admin.register(ProposalReview)
class ProposalReviewAdmin(admin.ModelAdmin):
    list_display = ("proposal", "reviewer", "decision", "created_at")
    autocomplete_fields = ("proposal", "reviewer")


@admin.register(ProposalDigitalSignature)
class ProposalDigitalSignatureAdmin(admin.ModelAdmin):
    autocomplete_fields = ("proposal", "signer")
