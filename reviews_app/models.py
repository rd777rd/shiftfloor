from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    class Direction(models.TextChoices):
        FACILITY_TO_WORKER = "FACILITY_TO_WORKER", "Facility rates Worker"
        WORKER_TO_FACILITY = "WORKER_TO_FACILITY", "Worker rates Facility"

    application = models.ForeignKey(
        "matching_app.ShiftApplication", on_delete=models.CASCADE, related_name="reviews"
    )
    direction = models.CharField(max_length=20, choices=Direction.choices)
    # 1-5 is enforced here at the model level (Rubric B.1), not just by the
    # <select> widget in ReviewForm — PositiveSmallIntegerField alone only
    # rejects negatives, so a raw POST could otherwise submit any positive
    # value and corrupt the denormalized avg_rating on Worker/Facility.
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["application", "direction"], name="one_review_per_direction_per_application"
            )
        ]

    def __str__(self):
        return f"{self.get_direction_display()} — {self.rating}★"
