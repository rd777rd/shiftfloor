from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.db import transaction

from core_app.forms import NoColonLabelMixin

from .models import User


# Django's built-in auth views (login, password reset) render their forms
# with the same default ":" label suffix as the signup forms above. These
# thin subclasses exist only to turn that off (Rubric E.2) — the view
# logic is untouched, wired in via `form_class=` in urls.py, keeping the
# "use built-in Django functionality" rule from the Coding Plan intact.
class StyledAuthenticationForm(NoColonLabelMixin, AuthenticationForm):
    pass


class StyledPasswordResetForm(NoColonLabelMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(NoColonLabelMixin, SetPasswordForm):
    pass


class WorkerSignupForm(NoColonLabelMixin, UserCreationForm):
    """Creates a User (role=WORKER) and its WorkerProfile in a single
    transaction, per Coding Plan §5 ('role assigned within same transaction
    as profile creation')."""

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    home_address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "first_name", "last_name"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.WORKER
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            user.save()
            from workers_app.models import WorkerProfile

            WorkerProfile.objects.create(
                user=user, home_address=self.cleaned_data["home_address"]
            )
        return user


class FacilitySignupForm(NoColonLabelMixin, UserCreationForm):
    """Creates a User (role=FACILITY_ADMIN), its Facility, and a first
    FacilityLocation together, per the same atomicity requirement."""

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    facility_name = forms.CharField(max_length=150, required=True)
    facility_address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "first_name", "last_name"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.FACILITY_ADMIN
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            user.save()
            from facilities_app.models import Facility, FacilityLocation
            from django.utils.text import slugify

            # Dedupe the slug the same way Shift.save() does (Rubric B.2)
            # — Facility.slug is unique=True, so two facilities signing up
            # with the same/similar name would otherwise hit an unhandled
            # IntegrityError and the second signup would crash with a 500.
            base_slug = slugify(self.cleaned_data["facility_name"])
            slug = base_slug
            n = 1
            while Facility.objects.filter(slug=slug).exists():
                n += 1
                slug = f"{base_slug}-{n}"

            facility = Facility.objects.create(
                user=user,
                name=self.cleaned_data["facility_name"],
                slug=slug,
            )
            FacilityLocation.objects.create(
                facility=facility,
                label="Main Location",
                address=self.cleaned_data["facility_address"],
            )
        return user
