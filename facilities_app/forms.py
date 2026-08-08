from django import forms

from core_app.forms import NoColonLabelMixin

from .models import Facility, FacilityLocation


class FacilityProfileForm(NoColonLabelMixin, forms.ModelForm):
    class Meta:
        model = Facility
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class FacilityLocationForm(NoColonLabelMixin, forms.ModelForm):
    class Meta:
        model = FacilityLocation
        fields = ["label", "address"]
