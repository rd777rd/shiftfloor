from django import forms

from core_app.forms import NoColonLabelMixin

from .models import Certification, WorkerProfile


class WorkerProfileForm(NoColonLabelMixin, forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ["bio", "home_address", "profile_photo"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}


class CertificationUploadForm(NoColonLabelMixin, forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["cert_type", "document"]
