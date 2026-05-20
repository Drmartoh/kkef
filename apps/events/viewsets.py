import secrets

from django.utils.text import slugify
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsForumAdminOrAbove

from .models import Event, RSVP
from .serializers import EventSerializer, RSVPSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().prefetch_related("rsvp_entries", "gallery")
    serializer_class = EventSerializer
    lookup_field = "slug"
    search_fields = ("title", "summary", "thematic_track")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        title = serializer.validated_data["title"]
        slug_val = slugify(title)[:220] or "event"
        n = 1
        base = slug_val
        while Event.objects.filter(slug=slug_val).exists():
            n += 1
            slug_val = f"{base}-{n}"

        qr_seed = secrets.token_hex(8)
        serializer.save(
            slug=slug_val,
            stewardship_lead=self.request.user,
            public_qr_seed=qr_seed,
        )

    def get_queryset(self):
        qs = super().get_queryset()
        track = getattr(self.request, "query_params", {}).get("track")
        if track:
            qs = qs.filter(thematic_track__iexact=track)
        upcoming_only = getattr(self.request, "query_params", {}).get("upcoming")
        if upcoming_only == "1":
            return qs.upcoming()
        return qs

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated()])
    def register(self, request, slug=None):
        event = self.get_object()
        companion_count = min(int(request.data.get("companions", 0)), 8)
        attendee_count = event.rsvp_entries.count()
        status_val = RSVP.Status.RESERVED
        if event.capacity and attendee_count >= event.capacity:
            status_val = RSVP.Status.WAITLISTED
        rsvp, created = RSVP.objects.get_or_create(
            event=event,
            attendee=request.user,
            defaults={
                "status": status_val,
                "companions": companion_count,
            },
        )
        if not created:
            rsvp.companions = companion_count
            rsvp.save(update_fields=["companions"])
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data)

    @action(detail=False, permission_classes=[permissions.AllowAny()])
    def calendar(self, request):
        queryset = Event.objects.upcoming().filter(is_public=True)[:120]
        return Response(EventSerializer(queryset, many=True).data)
