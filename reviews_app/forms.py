from django import forms

from core_app.forms import NoColonLabelMixin

from .models import Review


class ReviewForm(NoColonLabelMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
