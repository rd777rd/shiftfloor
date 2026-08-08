from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core_app.utils import haversine_miles


class Shift(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        FILLED = "FILLED", "Filled"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    location = models.ForeignKey(
        "facilities_app.FacilityLocation", on_delete=models.CASCADE, related_name="shifts"
    )
    role_type = models.CharField(max_length=30, choices=settings.CERTIFICATION_CHOICES)
    required_cert = models.CharField(
        max_length=30,
        choices=settings.CERTIFICATION_CHOICES,
        default="GENERAL",
        help_text="Certification a worker must hold VERIFIED to claim this shift.",
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    pay_rate = models.DecimalField(max_digits=6, decimal_places=2)
    headcount_needed = models.PositiveIntegerField(default=1)
    headcount_filled = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    auto_accept = models.BooleanField(
        default=False, help_text="Confirm applicants automatically without facility review."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_datetime"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_datetime"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.get_role_type_display()} @ {self.location} ({self.start_datetime:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(
                f"{self.role_type}-{self.location.label}-{self.start_datetime:%b-%d}"
            )
            slug = base
            n = 1
            while Shift.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shifts_app:shift_detail", args=[self.slug])

    @property
    def spots_remaining(self):
        return max(self.headcount_needed - self.headcount_filled, 0)

    @property
    def is_job_posting_eligible(self):
        """Drives whether the JobPosting JSON-LD renders on the detail page
        and whether the page is included in the sitemap. Stale JobPosting
        data can suppress site-wide Google for Jobs eligibility, so this is
        deliberately conservative — see SEO Plan §4 and Rubric B.11."""
        return self.status == self.Status.OPEN and self.start_datetime > timezone.now()

    def distance_from(self, lat, lng):
        return haversine_miles(lat, lng, self.location.lat, self.location.lng)
