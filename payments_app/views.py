import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from accounts_app.mixins import role_required
from accounts_app.models import User
from shifts_app.models import Shift

from .models import FacilityBillingProfile, Invoice, Payout, WorkerPayoutProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

# Flat per-shift placement fee for the facility-billing MVP — kept simple
# and explicit here rather than a subscription tier, per the Coding Plan.
PLACEMENT_FEE = 25.00


@role_required(User.Role.FACILITY_ADMIN)
def facility_billing(request):
    facility = request.user.facility
    billing_profile, _ = FacilityBillingProfile.objects.get_or_create(facility=facility)
    invoices = facility.invoices.order_by("-created_at")
    return render(
        request,
        "payments_app/facility_billing.html",
        {"billing_profile": billing_profile, "invoices": invoices, "fee": PLACEMENT_FEE},
    )


@role_required(User.Role.FACILITY_ADMIN)
def create_checkout_session(request, shift_id):
    """Kicks off a Stripe Checkout Session (test mode for the portfolio
    deployment, per Deployment Plan §7) for the flat placement fee on a
    shift the facility just filled.

    Ownership of the shift is verified the same way every other
    shift-scoped view in this codebase does it (Rubric A.1) — without
    this check, a facility admin could pass an arbitrary shift_id and
    have an invoice created against a shift they don't own."""
    facility = request.user.facility
    shift = get_object_or_404(Shift, pk=shift_id, location__facility=facility)
    invoice = Invoice.objects.create(facility=facility, shift=shift, amount=PLACEMENT_FEE)

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"ShiftFloor placement fee — shift #{shift_id}"},
                    "unit_amount": int(PLACEMENT_FEE * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=request.build_absolute_uri(reverse("payments_app:facility_billing")),
        cancel_url=request.build_absolute_uri(reverse("payments_app:facility_billing")),
        client_reference_id=str(invoice.id),
    )
    invoice.stripe_checkout_session_id = session.id
    invoice.save(update_fields=["stripe_checkout_session_id"])
    return redirect(session.url, permanent=False)


@role_required(User.Role.WORKER)
def worker_payouts(request):
    profile = request.user.worker_profile
    payout_profile, _ = WorkerPayoutProfile.objects.get_or_create(worker=profile)
    payouts = profile.payouts.order_by("-created_at")
    return render(
        request,
        "payments_app/worker_payouts.html",
        {"payout_profile": payout_profile, "payouts": payouts},
    )


@role_required(User.Role.WORKER)
def connect_onboarding(request):
    """Generates a Stripe Connect Express onboarding link so a worker can
    set up payouts, per Coding Plan §8."""
    profile = request.user.worker_profile
    payout_profile, _ = WorkerPayoutProfile.objects.get_or_create(worker=profile)

    if not payout_profile.stripe_connect_account_id:
        account = stripe.Account.create(type="express", email=request.user.email)
        payout_profile.stripe_connect_account_id = account.id
        payout_profile.save(update_fields=["stripe_connect_account_id"])

    account_link = stripe.AccountLink.create(
        account=payout_profile.stripe_connect_account_id,
        refresh_url=request.build_absolute_uri(reverse("payments_app:connect_onboarding")),
        return_url=request.build_absolute_uri(reverse("payments_app:worker_payouts")),
        type="account_onboarding",
    )
    return redirect(account_link.url)


@csrf_exempt
def stripe_webhook(request):
    """Verifies the Stripe signature before processing anything, per
    Rubric E.39 — an unverified webhook is a direct financial-data
    injection vector."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        invoice_id = session.get("client_reference_id")
        if invoice_id:
            Invoice.objects.filter(id=invoice_id).update(paid=True)

    elif event["type"] == "account.updated":
        account = event["data"]["object"]
        WorkerPayoutProfile.objects.filter(stripe_connect_account_id=account["id"]).update(
            payouts_enabled=account.get("payouts_enabled", False)
        )

    return HttpResponse(status=200)
