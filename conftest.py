"""
Shared fixtures for the whole suite. Factories create real DB rows, so any
fixture that touches one must declare `db` as a dependency — the lesson
learned the hard way on the Stonewick project (a fixture calling
request.session.save() failed without it; the same rule applies here to
any fixture that hits the database).
"""
from datetime import timedelta

import factory
import pytest
from django.utils import timezone

from accounts_app.models import User
from facilities_app.models import Facility, FacilityLocation
from workers_app.models import Certification, WorkerProfile
from shifts_app.models import Shift
from matching_app.models import ShiftApplication


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123!")
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class WorkerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkerProfile

    user = factory.SubFactory(UserFactory, role=User.Role.WORKER)
    home_address = "100 Main St, Indianapolis, IN"
    lat = 39.7684
    lng = -86.1581


class FacilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Facility

    user = factory.SubFactory(UserFactory, role=User.Role.FACILITY_ADMIN)
    name = factory.Sequence(lambda n: f"Test Facility {n}")
    slug = factory.Sequence(lambda n: f"test-facility-{n}")
    verified = True


class FacilityLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FacilityLocation

    facility = factory.SubFactory(FacilityFactory)
    label = "Main DC"
    address = "500 Airport Rd, Plainfield, IN"
    lat = 39.7942
    lng = -86.3789


class ShiftFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shift

    location = factory.SubFactory(FacilityLocationFactory)
    role_type = "FORKLIFT_III"
    required_cert = "FORKLIFT_III"
    start_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1, hours=8))
    pay_rate = "19.50"
    headcount_needed = 1
    auto_accept = False


class CertificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certification

    worker = factory.SubFactory(WorkerProfileFactory)
    cert_type = "FORKLIFT_III"
    status = Certification.Status.VERIFIED
    document = factory.django.FileField(filename="cert.pdf")


@pytest.fixture
def worker(db):
    return WorkerProfileFactory()


@pytest.fixture
def qualified_worker(db):
    """A worker with a VERIFIED Forklift Class III cert — matches
    ShiftFactory's default required_cert."""
    profile = WorkerProfileFactory()
    CertificationFactory(worker=profile, cert_type="FORKLIFT_III")
    return profile


@pytest.fixture
def facility(db):
    return FacilityFactory()


@pytest.fixture
def location(db, facility):
    return FacilityLocationFactory(facility=facility)


@pytest.fixture
def open_shift(db, location):
    return ShiftFactory(location=location, headcount_needed=1)
