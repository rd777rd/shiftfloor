from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core_app.utils import send_notification_email
from matching_app.models import ShiftApplication


class Command(BaseCommand):
    """Emails workers with a CONFIRMED application ~2 hours before their
    shift starts. Run every 15 minutes via a Render Cron Job."""

    help = "Send reminder emails for shifts starting in ~2 hours."

    REMINDER_WINDOW_MINUTES = 15

    def handle(self, *args, **options):
        now = timezone.now()
        window_start = now + timedelta(hours=2)
        window_end = window_start + timedelta(minutes=self.REMINDER_WINDOW_MINUTES)

        applications = ShiftApplication.objects.filter(
            status=ShiftApplication.Status.CONFIRMED,
            shift__start_datetime__gte=window_start,
            shift__start_datetime__lt=window_end,
        ).select_related("shift", "worker__user")

        sent = 0
        for application in applications:
            send_notification_email(
                subject=f"Reminder: your shift starts soon — {application.shift}",
                template_name="emails/shift_reminder.txt",
                context={"application": application},
                to_email=application.worker.user.email,
            )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminder(s)."))
