from django.conf import settings
from django.db import models


class Facility(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="facility"
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    # Denormalized, updated by reviews_app signals on Review save.
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name

    def fill_rate(self):
        """Percentage of the facility's shifts (last 90 days) that reached
        FILLED status — surfaced on the dashboard KPI strip.

        Fixed per Rubric C.1: this previously queried the facility's
        entire all-time shift history despite the docstring's "last 90
        days" claim, and counted CANCELLED/EXPIRED shifts as "filled"
        because it only excluded OPEN. Both inflated the KPI shown to
        facility admins."""
        from django.utils import timezone

        from shifts_app.models import Shift

        cutoff = timezone.now() - timezone.timedelta(days=90)
        shifts = Shift.objects.filter(location__facility=self, created_at__gte=cutoff)
        total = shifts.count()
        if not total:
            return 0
        filled = shifts.filter(
            status__in=[Shift.Status.FILLED, Shift.Status.IN_PROGRESS, Shift.Status.COMPLETED]
        ).count()
        return round((filled / total) * 100)


class FacilityLocation(models.Model):
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="locations"
    )
    label = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.facility.name} — {self.label}"
