"""Covers Rubric C.1 — Facility.fill_rate() must actually scope to the
last 90 days (per its own docstring) and must only count FILLED /
IN_PROGRESS / COMPLETED shifts as "filled" — not CANCELLED or EXPIRED."""
from datetime import timedelta

import pytest
from django.utils import timezone

from conftest import ShiftFactory
from shifts_app.models import Shift


@pytest.mark.django_db
def test_fill_rate_excludes_shifts_older_than_90_days(location):
    old_shift = ShiftFactory(location=location, status=Shift.Status.FILLED)
    Shift.objects.filter(pk=old_shift.pk).update(
        created_at=timezone.now() - timedelta(days=200)
    )
    ShiftFactory(location=location, status=Shift.Status.OPEN)  # recent, not filled

    # Only the recent OPEN shift should count — the 200-day-old FILLED
    # shift must be excluded, so fill rate should be 0%, not 100%.
    assert location.facility.fill_rate() == 0


@pytest.mark.django_db
def test_fill_rate_does_not_count_cancelled_or_expired_as_filled(location):
    ShiftFactory(location=location, status=Shift.Status.CANCELLED)
    ShiftFactory(location=location, status=Shift.Status.EXPIRED)
    ShiftFactory(location=location, status=Shift.Status.FILLED)

    # 1 of 3 shifts genuinely filled = 33%, not 100% (which the old
    # `.exclude(status="OPEN")` logic would have produced).
    assert location.facility.fill_rate() == 33


@pytest.mark.django_db
def test_fill_rate_counts_in_progress_and_completed_as_filled(location):
    ShiftFactory(location=location, status=Shift.Status.IN_PROGRESS)
    ShiftFactory(location=location, status=Shift.Status.COMPLETED)

    assert location.facility.fill_rate() == 100


@pytest.mark.django_db
def test_fill_rate_with_no_shifts_is_zero(facility):
    assert facility.fill_rate() == 0
