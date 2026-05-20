from django.contrib import admin

from .models import GalleryImage, NewsArticle, PhotoGallery, PressRelease, VideoAsset


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0


@admin.register(PhotoGallery)
class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "thematic_tag")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [GalleryImageInline]


@admin.register(VideoAsset)
class VideoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(NewsArticle)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary")


@admin.register(PressRelease)
class PressAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("headline",)}
