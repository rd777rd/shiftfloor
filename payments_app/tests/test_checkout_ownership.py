"""Covers Rubric A.1 — create_checkout_session must not let a facility
admin create an invoice against a shift they don't own."""
import pytest
from django.test import Client
from django.urls import reverse

from conftest import FacilityFactory, FacilityLocationFactory, ShiftFactory
from payments_app.models import Invoice


@pytest.mark.django_db
def test_facility_cannot_checkout_another_facilitys_shift(facility, open_shift):
    other_facility = FacilityFactory()
    other_location = FacilityLocationFactory(facility=other_facility)
    other_shift = ShiftFactory(location=other_location)

    client = Client()
    client.force_login(facility.user)  # logged in as `facility`, not the shift's owner
    response = client.post(
        reverse("payments_app:create_checkout_session", args=[other_shift.id])
    )

    assert response.status_code == 404
    assert not Invoice.objects.filter(shift=other_shift).exists()


@pytest.mark.django_db
def test_facility_can_checkout_its_own_shift(facility, open_shift, monkeypatch):
    # Stripe calls are network side effects out of scope for this test —
    # only the ownership gate matters here, so short-circuit the SDK call.
    class FakeSession:
        id = "cs_test_123"
        url = "https://checkout.stripe.com/fake"

    monkeypatch.setattr(
        "payments_app.views.stripe.checkout.Session.create", lambda **kwargs: FakeSession()
    )

    client = Client()
    client.force_login(facility.user)
    response = client.post(
        reverse("payments_app:create_checkout_session", args=[open_shift.id])
    )

    assert response.status_code == 302
    assert Invoice.objects.filter(shift=open_shift, facility=facility).exists()
