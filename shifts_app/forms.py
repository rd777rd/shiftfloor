from django import forms
from django.conf import settings

from .models import Shift


class ShiftForm(forms.ModelForm):
    """Single ModelForm backing the progressive-disclosure stepper UI —
    fields are grouped into JS-driven steps in the template
    (_shift_step_role.html, _shift_step_schedule.html, etc.) but validated
    together here server-side, per Coding Plan §7 and Design Plan Flow A."""

    class Meta:
        model = Shift
        fields = [
            "location",
            "role_type",
            "required_cert",
            "start_datetime",
            "end_datetime",
            "pay_rate",
            "headcount_needed",
            "auto_accept",
        ]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility is not None:
            self.fields["location"].queryset = facility.locations.all()

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_datetime")
        end = cleaned.get("end_datetime")
        if start and end and end <= start:
            raise forms.ValidationError("Shift end time must be after the start time.")
        return cleaned


class ShiftFilterForm(forms.Form):
    cert_type = forms.ChoiceField(
        choices=[("", "Any certification")] + settings.CERTIFICATION_CHOICES,
        required=False,
    )
    max_distance = forms.IntegerField(required=False, min_value=1, label="Within (miles)")
    min_pay = forms.DecimalField(required=False, min_value=0, label="Minimum pay ($/hr)")
