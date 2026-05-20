from django.shortcuts import render
from rest_framework import generics, permissions

from apps.accounts.serializers import UserSerializer


def profile_preferences(request):
    """Light-weight server render for OTP setup link from templates."""
    return render(request, "accounts/security_center.html")


class MeRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
