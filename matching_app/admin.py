from django.contrib import admin

from .models import ShiftApplication


@admin.register(ShiftApplication)
class ShiftApplicationAdmin(admin.ModelAdmin):
    list_display = ("worker", "shift", "status", "applied_at", "responded_at")
    list_filter = ("status",)
