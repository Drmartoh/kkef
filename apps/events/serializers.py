from rest_framework import serializers

from apps.events.models import Event, EventPhoto, EventTicket, RSVP


class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = "__all__"


class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = "__all__"


class EventPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    rsvps = RSVPSerializer(many=True, read_only=True, source="rsvp_entries")
    tickets = EventTicketSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("id", "slug", "created_at", "updated_at")
