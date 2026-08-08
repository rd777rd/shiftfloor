from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with a role flag. Role is set once at signup and
    drives which dashboard/templates/permissions apply (Coding Plan §4).
    Using Django's AbstractUser (not a full custom backend) keeps the
    built-in auth views usable as-is, per the project restriction to prefer
    built-in Django functionality."""

    class Role(models.TextChoices):
        WORKER = "WORKER", "Worker"
        FACILITY_ADMIN = "FACILITY_ADMIN", "Facility Admin"
        ADMIN = "ADMIN", "ShiftFloor Admin"

    role = models.CharField(max_length=20, choices=Role.choices)
    phone_number = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_worker(self):
        return self.role == self.Role.WORKER

    @property
    def is_facility_admin(self):
        return self.role == self.Role.FACILITY_ADMIN
