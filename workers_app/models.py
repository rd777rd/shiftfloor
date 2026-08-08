from django.conf import settings
from django.db import models

from .validators import validate_cert_document


class WorkerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worker_profile"
    )
    bio = models.TextField(blank=True)
    home_address = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to="worker_photos/", blank=True, null=True)

    # Denormalized for fast dashboard/profile reads — updated by
    # reviews_app signals on Review save (Coding Plan §3 & §5).
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completed_shifts_count = models.PositiveIntegerField(default=0)
    no_show_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WorkerProfile<{self.user.username}>"

    def verified_cert_types(self):
        """Set of cert_type codes this worker currently holds verified —
        the core input to the shift cert-gate check (Rubric C.20)."""
        return set(
            self.certifications.filter(status=Certification.Status.VERIFIED).values_list(
                "cert_type", flat=True
            )
        )

    def is_qualified_for(self, required_cert):
        if not required_cert or required_cert == "GENERAL":
            return True
        return required_cert in self.verified_cert_types()


class Certification(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="certifications"
    )
    cert_type = models.CharField(max_length=30, choices=settings.CERTIFICATION_CHOICES)
    document = models.FileField(
        upload_to="certifications/", validators=[validate_cert_document]
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_certifications",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_cert_type_display()} — {self.worker.user.username} ({self.status})"
