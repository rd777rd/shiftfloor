from django.contrib import admin

from .models import Facility, FacilityLocation


class FacilityLocationInline(admin.TabularInline):
    model = FacilityLocation
    extra = 0


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "verified", "avg_rating", "created_at")
    list_filter = ("verified",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FacilityLocationInline]
