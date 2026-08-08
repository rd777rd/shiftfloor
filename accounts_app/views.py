from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import FacilitySignupForm, WorkerSignupForm


class WorkerSignupView(CreateView):
    form_class = WorkerSignupForm
    template_name = "accounts_app/signup_worker.html"
    success_url = reverse_lazy("core_app:role_redirect")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class FacilitySignupView(CreateView):
    form_class = FacilitySignupForm
    template_name = "accounts_app/signup_facility.html"
    success_url = reverse_lazy("core_app:role_redirect")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


@login_required
def profile(request):
    """Role-aware profile view: redirects into the app-specific profile
    editor rather than duplicating profile-editing UI here."""
    if request.user.is_worker:
        return redirect("workers_app:profile_edit")
    if request.user.is_facility_admin:
        return redirect("facilities_app:profile_edit")
    return render(request, "accounts_app/profile.html")
