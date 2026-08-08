"""Covers Rubric B.2 — two facilities signing up with the same name must
not crash the second signup with an unhandled IntegrityError on
Facility.slug (unique=True)."""
import pytest

from accounts_app.forms import FacilitySignupForm
from facilities_app.models import Facility


def _signup_data(username):
    return {
        "username": username,
        "email": f"{username}@example.com",
        "phone_number": "3175551234",
        "first_name": "Pat",
        "last_name": "Owner",
        "facility_name": "Plainfield Logistics",
        "facility_address": "1 Airport Rd, Plainfield, IN",
        "password1": "testpass123!",
        "password2": "testpass123!",
    }


@pytest.mark.django_db
def test_duplicate_facility_name_gets_deduped_slug_not_a_crash():
    form1 = FacilitySignupForm(data=_signup_data("owner1"))
    assert form1.is_valid(), form1.errors
    form1.save()

    form2 = FacilitySignupForm(data=_signup_data("owner2"))
    assert form2.is_valid(), form2.errors
    form2.save()  # must not raise IntegrityError

    slugs = set(Facility.objects.filter(name="Plainfield Logistics").values_list("slug", flat=True))
    assert slugs == {"plainfield-logistics", "plainfield-logistics-2"}
