from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Review


@receiver(post_save, sender=Review)
def update_denormalized_ratings(sender, instance, **kwargs):
    """Recomputes avg_rating on the reviewed party whenever a Review is
    saved, per Coding Plan §5 / Rubric C.25. Recalculating from all
    reviews (rather than incrementally averaging) keeps this correct even
    if a review is ever edited or deleted."""
    application = instance.application

    if instance.direction == Review.Direction.FACILITY_TO_WORKER:
        worker = application.worker
        avg = Review.objects.filter(
            application__worker=worker, direction=Review.Direction.FACILITY_TO_WORKER
        ).aggregate(avg=Avg("rating"))["avg"]
        worker.avg_rating = round(avg or 0, 2)
        worker.save(update_fields=["avg_rating"])
    else:
        facility = application.shift.location.facility
        avg = Review.objects.filter(
            application__shift__location__facility=facility,
            direction=Review.Direction.WORKER_TO_FACILITY,
        ).aggregate(avg=Avg("rating"))["avg"]
        facility.avg_rating = round(avg or 0, 2)
        facility.save(update_fields=["avg_rating"])
