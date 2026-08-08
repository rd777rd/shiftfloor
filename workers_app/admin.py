from django.contrib import admin
from django.utils import timezone

from .models import Certification, WorkerProfile


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avg_rating", "completed_shifts_count", "no_show_count")
    search_fields = ("user__username", "user__email")


@admin.action(description="Mark selected certifications as VERIFIED")
def mark_verified(modeladmin, request, queryset):
    queryset.update(status=Certification.Status.VERIFIED, reviewed_by=request.user, reviewed_at=timezone.now())


@admin.action(description="Mark selected certifications as REJECTED")
def mark_rejected(modeladmin, request, queryset):
    queryset.update(status=Certification.Status.REJECTED, reviewed_by=request.user, reviewed_at=timezone.now())


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """This is the cert-verification queue referenced throughout the plans
    — admins filter by PENDING and bulk-approve/reject."""

    list_display = ("worker", "cert_type", "status", "uploaded_at", "reviewed_by")
    list_filter = ("status", "cert_type")
    actions = [mark_verified, mark_rejected]
