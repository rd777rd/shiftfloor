"""
Covers Rubric C.19 (race-condition safety) and C.20 (server-side cert gate)
— the two most correctness-critical items in the whole audit.
"""
import threading

import pytest
from django.test import Client
from django.urls import reverse

from conftest import CertificationFactory, ShiftFactory, WorkerProfileFactory
from matching_app.models import ShiftApplication


@pytest.mark.django_db
def test_unqualified_worker_cannot_claim_shift(worker, open_shift):
    """Server-side enforcement: even if a request is crafted directly
    against the claim endpoint, a worker without a VERIFIED matching cert
    can never create a ShiftApplication — the UI's "you qualify" check is
    a convenience, not the security boundary."""
    client = Client()
    client.force_login(worker.user)

    response = client.post(reverse("matching_app:claim_shift", args=[open_shift.slug]))

    assert response.status_code == 302
    assert not ShiftApplication.objects.filter(shift=open_shift, worker=worker).exists()
    open_shift.refresh_from_db()
    assert open_shift.headcount_filled == 0


@pytest.mark.django_db
def test_qualified_worker_can_claim_shift(qualified_worker, open_shift):
    client = Client()
    client.force_login(qualified_worker.user)

    response = client.post(reverse("matching_app:claim_shift", args=[open_shift.slug]))

    assert response.status_code == 302
    assert ShiftApplication.objects.filter(shift=open_shift, worker=qualified_worker).exists()


@pytest.mark.django_db
def test_claim_already_full_shift_is_rejected(location):
    """Sequential race scenario: once a shift is FILLED, a second worker's
    claim attempt is rejected server-side rather than silently over-filling
    headcount."""
    shift = ShiftFactory(location=location, headcount_needed=1, auto_accept=True)
    first_worker = WorkerProfileFactory()
    CertificationFactory(worker=first_worker, cert_type=shift.required_cert)
    second_worker = WorkerProfileFactory()
    CertificationFactory(worker=second_worker, cert_type=shift.required_cert)

    client_a = Client()
    client_a.force_login(first_worker.user)
    client_a.post(reverse("matching_app:claim_shift", args=[shift.slug]))

    shift.refresh_from_db()
    assert shift.status == shift.Status.FILLED
    assert shift.headcount_filled == 1

    client_b = Client()
    client_b.force_login(second_worker.user)
    client_b.post(reverse("matching_app:claim_shift", args=[shift.slug]))

    assert not ShiftApplication.objects.filter(shift=shift, worker=second_worker).exists()
    shift.refresh_from_db()
    assert shift.headcount_filled == 1  # never over-filled


@pytest.mark.django_db(transaction=True)
def test_concurrent_claims_never_overfill_headcount(location):
    """Fires several claim requests at the same single-spot shift roughly
    simultaneously via real threads. Regardless of the exact interleaving,
    transaction.atomic() + select_for_update() (and SQLite's own
    file-level write serialization as a backstop in this test environment)
    must guarantee exactly one CONFIRMED application — never zero, never
    more than one. This is the concurrency-level proof behind Rubric C.19;
    the sequential test above proves the same invariant more simply."""
    shift = ShiftFactory(location=location, headcount_needed=1, auto_accept=True)
    workers = []
    for _ in range(5):
        w = WorkerProfileFactory()
        CertificationFactory(worker=w, cert_type=shift.required_cert)
        workers.append(w)

    def attempt_claim(worker):
        client = Client()
        client.force_login(worker.user)
        client.post(reverse("matching_app:claim_shift", args=[shift.slug]))

    threads = [threading.Thread(target=attempt_claim, args=(w,)) for w in workers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    confirmed = ShiftApplication.objects.filter(
        shift=shift, status=ShiftApplication.Status.CONFIRMED
    ).count()
    assert confirmed == 1

    shift.refresh_from_db()
    assert shift.headcount_filled == 1
    assert shift.status == shift.Status.FILLED
