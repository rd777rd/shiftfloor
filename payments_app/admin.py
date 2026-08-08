from django.contrib import admin

from .models import FacilityBillingProfile, Invoice, Payout, WorkerPayoutProfile

admin.site.register(FacilityBillingProfile)
admin.site.register(WorkerPayoutProfile)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("facility", "amount", "paid", "created_at")
    list_filter = ("paid",)


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("worker", "amount", "created_at")
