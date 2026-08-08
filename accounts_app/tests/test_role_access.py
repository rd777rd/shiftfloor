"""Covers Rubric E.36 — RoleRequiredMixin / role_required must block every
cross-role view, not just hide the nav link to it."""
import pytest
from django.test import Client
from django.urls import reverse

from conftest import FacilityFactory, WorkerProfileFactory


@pytest.mark.django_db
def test_worker_cannot_access_shift_post(worker):
    client = Client()
    client.force_login(worker.user)
    response = client.get(reverse("shifts_app:shift_post"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_worker_cannot_access_facility_dashboard(worker):
    client = Client()
    client.force_login(worker.user)
    response = client.get(reverse("facilities_app:dashboard"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_facility_admin_cannot_access_worker_dashboard(facility):
    client = Client()
    client.force_login(facility.user)
    response = client.get(reverse("workers_app:dashboard"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login(client):
    response = client.get(reverse("facilities_app:dashboard"))
    assert response.status_code == 302
    assert reverse("accounts_app:login") in response.url


@pytest.mark.django_db
def test_facility_admin_can_access_own_dashboard(facility):
    client = Client()
    client.force_login(facility.user)
    response = client.get(reverse("facilities_app:dashboard"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_worker_can_access_own_dashboard(worker):
    client = Client()
    client.force_login(worker.user)
    response = client.get(reverse("workers_app:dashboard"))
    assert response.status_code == 200
