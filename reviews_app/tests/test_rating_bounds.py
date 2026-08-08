"""Covers Rubric B.1 — Review.rating must reject out-of-range values
server-side, not rely on the <select> widget in ReviewForm to constrain
what gets submitted."""
import pytest
from django.core.exceptions import ValidationError

from conftest import ShiftFactory
from matching_app.models import ShiftApplication
from reviews_app.forms import ReviewForm
from reviews_app.models import Review


@pytest.mark.parametrize("bad_rating", [0, -1, 6, 999])
def test_form_rejects_out_of_range_rating(bad_rating):
    form = ReviewForm(data={"rating": bad_rating, "comment": "x"})
    assert not form.is_valid()
    assert "rating" in form.errors


@pytest.mark.parametrize("good_rating", [1, 2, 3, 4, 5])
def test_form_accepts_boundary_ratings(good_rating):
    form = ReviewForm(data={"rating": good_rating, "comment": "x"})
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_model_full_clean_rejects_out_of_range_rating(worker, location):
    shift = ShiftFactory(location=location)
    application = ShiftApplication.objects.create(
        shift=shift, worker=worker, status=ShiftApplication.Status.COMPLETED
    )
    review = Review(
        application=application,
        direction=Review.Direction.FACILITY_TO_WORKER,
        rating=999,
    )
    with pytest.raises(ValidationError):
        review.full_clean()
