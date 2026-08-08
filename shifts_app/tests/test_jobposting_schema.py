"""Covers Rubric B.10 (valid JobPosting JSON-LD) and B.11 (expired/filled
shifts must not emit stale JobPosting data)."""
import json
from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from conftest import ShiftFactory
from shifts_app.models import Shift
from shifts_app.templatetags.jobposting_tags import jobposting_jsonld

REQUIRED_FIELDS = {
    "title",
    "description",
    "datePosted",
    "validThrough",
    "employmentType",
    "hiringOrganization",
    "jobLocation",
    "baseSalary",
}


@pytest.mark.django_db
def test_open_future_shift_emits_valid_jobposting_jsonld(location):
    shift = ShiftFactory(location=location, status=Shift.Status.OPEN)

    output = jobposting_jsonld(shift)
    assert output != ""

    data = json.loads(str(output).split(">", 1)[1].rsplit("<", 1)[0])
    assert data["@type"] == "JobPosting"
    assert REQUIRED_FIELDS.issubset(data.keys())
    assert data["employmentType"] == "TEMPORARY"
    assert data["baseSalary"]["value"]["value"] == float(shift.pay_rate)


@pytest.mark.django_db
def test_expired_shift_emits_no_jobposting_jsonld(location):
    shift = ShiftFactory(
        location=location,
        status=Shift.Status.EXPIRED,
        start_datetime=timezone.now() - timedelta(days=1),
        end_datetime=timezone.now() - timedelta(hours=16),
    )
    assert jobposting_jsonld(shift) == ""


@pytest.mark.django_db
def test_filled_shift_emits_no_jobposting_jsonld(location):
    shift = ShiftFactory(location=location, status=Shift.Status.FILLED)
    assert jobposting_jsonld(shift) == ""


@pytest.mark.django_db
def test_shift_detail_page_includes_jobposting_script_tag(location):
    shift = ShiftFactory(location=location, status=Shift.Status.OPEN)
    client = Client()
    response = client.get(reverse("shifts_app:shift_detail", args=[shift.slug]))
    assert response.status_code == 200
    assert b'"@type": "JobPosting"' in response.content
