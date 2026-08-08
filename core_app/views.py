from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from shifts_app.models import Shift


class HomeView(TemplateView):
    """Split hero for facility vs. worker intent, per Design Plan §6.
    Shows a live count of currently open shifts as a trust/urgency signal."""

    template_name = "core_app/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["open_shift_count"] = Shift.objects.filter(status="OPEN").count()
        return ctx


class HowItWorksView(TemplateView):
    template_name = "core_app/how_it_works.html"


class CertificationsInfoView(TemplateView):
    template_name = "core_app/certifications_info.html"


class PricingView(TemplateView):
    template_name = "core_app/pricing.html"


class FaqView(TemplateView):
    template_name = "core_app/faq.html"

    FAQS = [
        (
            "What certifications does ShiftFloor accept?",
            "We accept forklift certifications (Classes I through VII), "
            "OSHA 10, and OSHA 30. General labor shifts require no "
            "certification.",
        ),
        (
            "How fast can a facility fill an open shift?",
            "Once a shift is posted, it's immediately visible to matching, "
            "verified workers. Most shifts posted before 9am are filled by "
            "lunch.",
        ),
        (
            "Is there a fee for workers to use ShiftFloor?",
            "No — browsing and claiming shifts is always free for workers. "
            "Facilities pay a per-shift placement fee.",
        ),
        (
            "How are certifications verified?",
            "Workers upload a photo or PDF of their certification during "
            "signup. Our team reviews and verifies each one before the "
            "worker can claim a shift requiring that certification.",
        ),
    ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["faqs"] = self.FAQS
        return ctx


class ContactView(TemplateView):
    template_name = "core_app/contact.html"


@login_required
def role_redirect(request):
    """Sends a freshly logged-in user to the correct dashboard for their
    role, per Coding Plan §4 (role-based routing)."""
    user = request.user
    if user.role == user.Role.FACILITY_ADMIN:
        return redirect("facilities_app:dashboard")
    if user.role == user.Role.WORKER:
        return redirect("workers_app:dashboard")
    return redirect("core_app:home")
