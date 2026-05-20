from django.contrib import admin

from .models import Event, EventPhoto, EventTicket, RSVP


class RSVPInline(admin.TabularInline):
    model = RSVP
    extra = 0


class EventGalleryInline(admin.TabularInline):
    model = EventPhoto
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_at", "is_public")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    autocomplete_fields = ("organizer_group", "stewardship_lead")
    inlines = [RSVPInline, EventGalleryInline]


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = ("event", "holder", "code", "status")


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("event", "attendee", "status")
