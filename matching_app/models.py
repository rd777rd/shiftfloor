from django.db import models


class ShiftApplication(models.Model):
    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        OFFERED = "OFFERED", "Offered"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        NO_SHOW = "NO_SHOW", "No-show"
        CANCELLED = "CANCELLED", "Cancelled"

    shift = models.ForeignKey(
        "shifts_app.Shift", on_delete=models.CASCADE, related_name="applications"
    )
    worker = models.ForeignKey(
        "workers_app.WorkerProfile", on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.APPLIED)
    applied_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shift", "worker"], name="unique_application_per_worker_per_shift"
            )
        ]

    def __str__(self):
        return f"{self.worker} → {self.shift} ({self.status})"
