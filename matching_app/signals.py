from django.db.models.signals import post_save
from django.dispatch import receiver

from shifts_app.models import Shift

from .models import ShiftApplication


@receiver(post_save, sender=ShiftApplication)
def sync_shift_headcount(sender, instance, **kwargs):
    """Keeps Shift.headcount_filled and Shift.status in sync whenever an
    application reaches CONFIRMED, per Coding Plan §5 / Rubric C.22.
    Recalculates from a fresh count rather than incrementing, so this stays
    correct even if an application's status changes more than once."""
    shift = instance.shift
    confirmed_count = shift.applications.filter(status=ShiftApplication.Status.CONFIRMED).count()

    update_fields = []
    if shift.headcount_filled != confirmed_count:
        shift.headcount_filled = confirmed_count
        update_fields.append("headcount_filled")

    if confirmed_count >= shift.headcount_needed and shift.status == Shift.Status.OPEN:
        shift.status = Shift.Status.FILLED
        update_fields.append("status")
    elif confirmed_count < shift.headcount_needed and shift.status == Shift.Status.FILLED:
        # A confirmed worker backed out — reopen the shift so it's
        # matchable again rather than silently sitting understaffed.
        shift.status = Shift.Status.OPEN
        update_fields.append("status")

    if update_fields:
        shift.save(update_fields=update_fields)


@receiver(post_save, sender=ShiftApplication)
def sync_worker_shift_counts(sender, instance, **kwargs):
    """Keeps WorkerProfile.completed_shifts_count / no_show_count current
    whenever an application resolves to COMPLETED or NO_SHOW — these feed
    the trust snapshot on the worker's public profile (Design Plan §6)."""
    if instance.status not in (ShiftApplication.Status.COMPLETED, ShiftApplication.Status.NO_SHOW):
        return
    worker = instance.worker
    worker.completed_shifts_count = worker.applications.filter(
        status=ShiftApplication.Status.COMPLETED
    ).count()
    worker.no_show_count = worker.applications.filter(
        status=ShiftApplication.Status.NO_SHOW
    ).count()
    worker.save(update_fields=["completed_shifts_count", "no_show_count"])
