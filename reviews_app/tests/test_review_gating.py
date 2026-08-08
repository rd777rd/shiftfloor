import pytest
from django.test import Client
from django.urls import reverse

from conftest import ShiftFactory
from matching_app.models import ShiftApplication
from reviews_app.models import Review


@pytest.mark.django_db
def test_review_blocked_until_shift_completed(worker, location):
    shift = ShiftFactory(location=location)
    application = ShiftApplication.objects.create(
        shift=shift, worker=worker, status=ShiftApplication.Status.CONFIRMED
    )
    client = Client()
    client.force_login(worker.user)

    response = client.get(reverse("reviews_app:submit_review", args=[application.id]))

    assert response.status_code == 302
    assert not Review.objects.filter(application=application).exists()


@pytest.mark.django_db
def test_review_allowed_once_completed_and_only_once(worker, location):
    shift = ShiftFactory(location=location)
    application = ShiftApplication.objects.create(
        shift=shift, worker=worker, status=ShiftApplication.Status.COMPLETED
    )
    client = Client()
    client.force_login(worker.user)

    client.post(
        reverse("reviews_app:submit_review", args=[application.id]),
        {"rating": 5, "comment": "Great shift"},
    )
    assert Review.objects.filter(application=application).count() == 1

    # A second submission for the same application/direction must not
    # create a duplicate review.
    client.post(
        reverse("reviews_app:submit_review", args=[application.id]),
        {"rating": 1, "comment": "duplicate attempt"},
    )
    assert Review.objects.filter(application=application).count() == 1
