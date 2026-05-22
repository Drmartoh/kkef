from django.core.management.base import BaseCommand

from apps.core.models import ForumOfficial


class Command(BaseCommand):
    help = "Resize existing official portrait uploads to the standard headshot size."

    def handle(self, *args, **options):
        qs = ForumOfficial.objects.exclude(photo="")
        total = qs.count()
        if not total:
            self.stdout.write("No official photos to process.")
            return

        done = 0
        for official in qs.iterator():
            official.save(reprocess_photo=True)
            done += 1
            self.stdout.write(f"  Resized: {official.name}")

        self.stdout.write(self.style.SUCCESS(f"Processed {done} of {total} portrait(s)."))
