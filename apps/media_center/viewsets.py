from rest_framework import permissions, viewsets

from apps.accounts.permissions import IsForumAdminOrAbove

from .models import GalleryImage, NewsArticle, PhotoGallery, PressRelease, VideoAsset
from .serializers import (
    GalleryImageSerializer,
    NewsArticleSerializer,
    PhotoGallerySerializer,
    PressReleaseSerializer,
    VideoAssetSerializer,
)


class PhotoGalleryViewSet(viewsets.ModelViewSet):
    queryset = PhotoGallery.objects.prefetch_related("images").order_by("-created_at")
    serializer_class = PhotoGallerySerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]


class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsForumAdminOrAbove]


class VideoAssetViewSet(viewsets.ModelViewSet):
    queryset = VideoAsset.objects.order_by("-created_at")
    serializer_class = VideoAssetSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]


class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.order_by("-created_at")
    serializer_class = NewsArticleSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]

    def get_queryset(self):
        qs = super().get_queryset()
        params = getattr(self.request, "query_params", {})
        user = getattr(self.request, "user", None)
        if params.get("include_drafts") == "1" and user and user.is_authenticated:
            return qs
        return qs.filter(status=NewsArticle.Status.PUBLISHED)


class PressReleaseViewSet(viewsets.ModelViewSet):
    queryset = PressRelease.objects.order_by("-created_at")
    serializer_class = PressReleaseSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsForumAdminOrAbove()]
