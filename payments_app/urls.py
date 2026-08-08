from django.urls import path

from . import views

app_name = "payments_app"

urlpatterns = [
    path("facility/billing/", views.facility_billing, name="facility_billing"),
    path(
        "facility/checkout/<int:shift_id>/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("worker/payouts/", views.worker_payouts, name="worker_payouts"),
    path("worker/connect/", views.connect_onboarding, name="connect_onboarding"),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe_webhook"),
]
