"""Serializers for in-dashboard CRUD (multipart-friendly)."""

from django.utils.text import slugify
from rest_framework import serializers

from apps.accounts.models import User
from apps.core.kiambu_data import GROUP_APPLICATION_TYPE_CHOICES, KIAMBU_WARD_CHOICES
from apps.core.models import ForumOfficial
from apps.events.models import Event
from apps.funding.models import Donation, DonorIntake
from apps.media_center.models import NewsArticle
from apps.organizations.models import CommunityGroup, GroupJoinApplication
from apps.projects.models import Project, ProjectMedia, ProjectMilestone
from apps.documents.models import Document
from apps.proposals.models import Proposal


def _unique_slug(model, title: str, instance=None) -> str:
    base = slugify(title)[:200] or "item"
    slug_val = base
    n = 1
    qs = model.objects.all()
    if instance:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug_val).exists():
        n += 1
        slug_val = f"{base}-{n}"
    return slug_val


class ChoiceOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class ManageMetaSerializer(serializers.Serializer):
    project_statuses = ChoiceOptionSerializer(many=True)
    proposal_statuses = ChoiceOptionSerializer(many=True)
    news_statuses = ChoiceOptionSerializer(many=True)
    group_types = ChoiceOptionSerializer(many=True)
    wards = ChoiceOptionSerializer(many=True)
    groups = serializers.ListField()
    users = serializers.ListField()


class ForumOfficialManageSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    focus_areas_text = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ForumOfficial
        fields = (
            "id",
            "tier",
            "name",
            "role",
            "tagline",
            "bio",
            "tenure",
            "focus_areas",
            "focus_areas_text",
            "photo",
            "photo_url",
            "sort_order",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "photo_url")

    def get_photo_url(self, obj):
        return obj.photo_url

    def validate(self, attrs):
        text = attrs.pop("focus_areas_text", None)
        if text is not None:
            attrs["focus_areas"] = [t.strip() for t in text.split(",") if t.strip()]
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["focus_areas_text"] = ", ".join(instance.focus_areas or [])
        return data


class ProjectMediaManageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMedia
        fields = (
            "id",
            "project",
            "media_type",
            "image",
            "image_url",
            "video_url",
            "caption",
            "tags",
            "taken_on",
            "sort_order",
            "is_featured",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "image_url")

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ""


class ProjectMilestoneManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProjectManageSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    media_items = ProjectMediaManageSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneManageSerializer(many=True, read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True, default="")
    intervention_tags_text = serializers.CharField(required=False, allow_blank=True, write_only=True)
    sdg_goals_text = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "reference_code",
            "title",
            "slug",
            "group",
            "group_name",
            "description",
            "problem_statement",
            "anticipated_outcomes",
            "budget_total",
            "funding_secured",
            "timeline_start",
            "timeline_end",
            "location",
            "latitude",
            "longitude",
            "wards_served",
            "sdg_goals",
            "sdg_goals_text",
            "beneficiaries_count",
            "intervention_tags",
            "intervention_tags_text",
            "transparency_summary",
            "status",
            "progress_percentage",
            "cover_image",
            "cover_image_url",
            "spotlight_video_url",
            "steward",
            "media_items",
            "milestones",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at", "cover_image_url", "media_items", "milestones")

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return ""

    def _apply_tags(self, attrs):
        tags = attrs.pop("intervention_tags_text", None)
        if tags is not None:
            attrs["intervention_tags"] = tags.strip()
        sdg = attrs.pop("sdg_goals_text", None)
        if sdg is not None:
            attrs["sdg_goals"] = [t.strip() for t in sdg.split(",") if t.strip()]
        return attrs

    def validate(self, attrs):
        return self._apply_tags(attrs)

    def create(self, validated_data):
        title = validated_data.get("title", "")
        validated_data["slug"] = _unique_slug(Project, title)
        if not validated_data.get("reference_code"):
            validated_data["reference_code"] = validated_data["slug"][:32].upper()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "title" in validated_data and validated_data["title"] != instance.title:
            validated_data.setdefault("slug", _unique_slug(Project, validated_data["title"], instance))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["intervention_tags_text"] = instance.intervention_tags or ""
        data["sdg_goals_text"] = ", ".join(instance.sdg_goals or [])
        return data


class CommunityGroupManageSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    thematic_focus_tags_text = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = CommunityGroup
        fields = (
            "id",
            "name",
            "slug",
            "group_type",
            "motto",
            "logo",
            "logo_url",
            "registration_number",
            "ward",
            "summary",
            "narrative",
            "thematic_focus_tags",
            "thematic_focus_tags_text",
            "is_published",
            "is_featured",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at", "logo_url")

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return ""

    def validate(self, attrs):
        text = attrs.pop("thematic_focus_tags_text", None)
        if text is not None:
            attrs["thematic_focus_tags"] = text.strip()
        return attrs

    def create(self, validated_data):
        validated_data["slug"] = _unique_slug(CommunityGroup, validated_data.get("name", ""))
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["thematic_focus_tags_text"] = instance.thematic_focus_tags or ""
        return data


class EventManageSerializer(serializers.ModelSerializer):
    hero_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "slug",
            "title",
            "summary",
            "narrative",
            "thematic_track",
            "hero_image",
            "hero_image_url",
            "start_at",
            "end_at",
            "venue_descriptor",
            "latitude",
            "longitude",
            "organizer_group",
            "is_public",
            "volunteering_open",
            "capacity",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at", "hero_image_url")

    def get_hero_image_url(self, obj):
        if obj.hero_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.hero_image.url)
            return obj.hero_image.url
        return ""

    def create(self, validated_data):
        validated_data["slug"] = _unique_slug(Event, validated_data.get("title", ""))
        return super().create(validated_data)


class NewsArticleManageSerializer(serializers.ModelSerializer):
    hero_image_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = (
            "id",
            "title",
            "slug",
            "summary",
            "body",
            "hero_image",
            "hero_image_url",
            "status",
            "tags_csv",
            "authored_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "hero_image_url")

    def get_hero_image_url(self, obj):
        if obj.hero_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.hero_image.url)
            return obj.hero_image.url
        return ""

    def create(self, validated_data):
        validated_data["slug"] = _unique_slug(NewsArticle, validated_data.get("title", ""))
        return super().create(validated_data)


class ProposalManageSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="owning_group.name", read_only=True)

    class Meta:
        model = Proposal
        fields = (
            "id",
            "reference",
            "slug",
            "title",
            "owning_group",
            "group_name",
            "category",
            "synopsis",
            "status",
            "projected_budget",
            "beneficiaries_estimate",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "reference", "slug", "created_at", "updated_at", "group_name")


class DonorIntakeManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorIntake
        fields = "__all__"
        read_only_fields = ("reference", "created_at", "updated_at")


class GroupJoinApplicationManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupJoinApplication
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class DonationManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = (
            "id",
            "reference",
            "amount",
            "currency",
            "channel",
            "status",
            "ledger_note",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DocumentManageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    project_title = serializers.CharField(source="project.title", read_only=True, default="")
    group_name = serializers.CharField(source="group.name", read_only=True, default="")

    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "slug",
            "doc_type",
            "visibility",
            "group",
            "group_name",
            "project",
            "project_title",
            "proposal",
            "file",
            "file_url",
            "mime_type",
            "version_label",
            "confidentiality_note",
            "uploaded_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at", "file_url", "uploaded_by")

    def get_file_url(self, obj):
        if not obj.file:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def validate(self, attrs):
        if not self.instance and not attrs.get("file"):
            raise serializers.ValidationError({"file": "Upload a file for new documents."})
        return attrs

    def create(self, validated_data):
        validated_data["slug"] = _unique_slug(Document, validated_data.get("title", ""))
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["uploaded_by"] = request.user
        upload = validated_data.get("file")
        if upload and hasattr(upload, "content_type"):
            validated_data.setdefault("mime_type", upload.content_type or "")
        return super().create(validated_data)


class UserManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "is_active",
            "is_staff",
        )
        read_only_fields = ("id",)
