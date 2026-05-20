import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectMedia",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "media_type",
                    models.CharField(
                        choices=[("photo", "Photo"), ("video", "Video link")],
                        default="photo",
                        max_length=16,
                    ),
                ),
                ("image", models.ImageField(blank=True, upload_to="project_media/gallery/")),
                ("video_url", models.URLField(blank=True)),
                ("caption", models.CharField(blank=True, max_length=255)),
                ("tags", models.CharField(blank=True, help_text="Comma-separated tags", max_length=255)),
                ("taken_on", models.DateField(blank=True, null=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_featured", models.BooleanField(default=False)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media_items",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "-created_at"],
            },
        ),
    ]
