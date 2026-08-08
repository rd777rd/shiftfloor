from django.contrib import admin

from .models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
        "headcount_filled",
        "headcount_needed",
        "pay_rate",
        "start_datetime",
    )
    list_filter = ("status", "role_type", "required_cert")
    search_fields = ("location__facility__name", "location__label")
