from django.conf import settings
from django.db import models


class FacilityBillingProfile(models.Model):
    facility = models.OneToOneField(
        "facilities_app.Facility", on_delete=models.CASCADE, related_name="billing_profile"
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Billing<{self.facility.name}>"


class WorkerPayoutProfile(models.Model):
    worker = models.OneToOneField(
        "workers_app.WorkerProfile", on_delete=models.CASCADE, related_name="payout_profile"
    )
    stripe_connect_account_id = models.CharField(max_length=255, blank=True)
    payouts_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"Payouts<{self.worker.user.username}>"


class Invoice(models.Model):
    """One row per facility placement-fee charge (a Stripe Checkout Session)."""

    facility = models.ForeignKey("facilities_app.Facility", on_delete=models.CASCADE, related_name="invoices")
    shift = models.ForeignKey("shifts_app.Shift", on_delete=models.SET_NULL, null=True, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.pk} — {self.facility.name} — ${self.amount}"


class Payout(models.Model):
    """One row per worker payout event (a Stripe Connect transfer)."""

    worker = models.ForeignKey("workers_app.WorkerProfile", on_delete=models.CASCADE, related_name="payouts")
    application = models.ForeignKey("matching_app.ShiftApplication", on_delete=models.SET_NULL, null=True, blank=True)
    stripe_transfer_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payout #{self.pk} — {self.worker.user.username} — ${self.amount}"
