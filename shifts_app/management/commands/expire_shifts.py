from django.core.management.base import BaseCommand
from django.utils import timezone

from shifts_app.models import Shift


class Command(BaseCommand):
    """Flips any OPEN shift whose start_datetime has passed to EXPIRED.
    Run hourly via a Render Cron Job. This is what keeps JobPosting
    structured data and the sitemap free of stale listings — see SEO
    Plan §4/§6 and Deployment Plan §6."""

    help = "Expire OPEN shifts whose start time has passed."

    def handle(self, *args, **options):
        stale = Shift.objects.filter(status=Shift.Status.OPEN, start_datetime__lt=timezone.now())
        count = stale.update(status=Shift.Status.EXPIRED)
        self.stdout.write(self.style.SUCCESS(f"Expired {count} shift(s)."))
