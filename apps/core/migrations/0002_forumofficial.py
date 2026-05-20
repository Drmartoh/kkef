from django.db import migrations, models


def seed_forum_officials(apps, schema_editor):
    from apps.core.officials import DEFAULT_OFFICIALS

    ForumOfficial = apps.get_model("core", "ForumOfficial")
    if ForumOfficial.objects.exists():
        return
    rows = []
    for row in DEFAULT_OFFICIALS:
        payload = dict(row)
        payload["tier"] = payload["tier"].value if hasattr(payload["tier"], "value") else payload["tier"]
        rows.append(ForumOfficial(**payload))
    ForumOfficial.objects.bulk_create(rows)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ForumOfficial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tier",
                    models.CharField(
                        choices=[("executive", "Executive board"), ("extended", "Extended secretariat")],
                        db_index=True,
                        max_length=16,
                    ),
                ),
                ("name", models.CharField(max_length=160)),
                ("role", models.CharField(max_length=120)),
                ("tagline", models.CharField(blank=True, max_length=200)),
                ("bio", models.TextField()),
                ("tenure", models.CharField(blank=True, max_length=200)),
                ("focus_areas", models.JSONField(blank=True, default=list)),
                ("photo", models.ImageField(blank=True, upload_to="officials/%Y/%m/")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
            ],
            options={
                "verbose_name": "forum official",
                "verbose_name_plural": "forum officials",
                "ordering": ["tier", "sort_order", "name"],
            },
        ),
        migrations.RunPython(seed_forum_officials, migrations.RunPython.noop),
    ]
