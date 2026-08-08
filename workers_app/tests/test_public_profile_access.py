"""Covers Rubric A.2 — worker_public_profile must not be reachable by an
anonymous visitor or by a worker; only facility admins are the intended
audience per the view's own docstring."""
import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_anonymous_visitor_is_redirected_to_login(worker):
    client = Client()
    response = client.get(
        reverse("workers_app:worker_public_profile", args=[worker.pk])
    )
    assert response.status_code == 302
    assert reverse("accounts_app:login") in response.url


@pytest.mark.django_db
def test_worker_cannot_view_another_workers_profile(worker):
    from conftest import WorkerProfileFactory

    other_worker = WorkerProfileFactory()
    client = Client()
    client.force_login(worker.user)
    response = client.get(
        reverse("workers_app:worker_public_profile", args=[other_worker.pk])
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_facility_admin_can_view_worker_profile(worker, facility):
    client = Client()
    client.force_login(facility.user)
    response = client.get(
        reverse("workers_app:worker_public_profile", args=[worker.pk])
    )
    assert response.status_code == 200
