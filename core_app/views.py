import hmac
from io import StringIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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


def _run_internal_task(request, command_name):
    """Shared handler for the scheduled-task endpoints below. Auth is a
    shared secret (INTERNAL_TASK_KEY) sent as a header, checked with
    hmac.compare_digest to avoid a timing side-channel. These endpoints
    exist because the app now runs on SQLite (see settings/base.py) — a
    local file GitHub Actions' runners can't reach directly, so the
    scheduled workflow calls the command in-process here instead."""
    expected = settings.INTERNAL_TASK_KEY
    provided = request.headers.get("X-Task-Key", "")
    if not expected or not hmac.compare_digest(expected, provided):
        return HttpResponseForbidden("forbidden")
    out = StringIO()
    call_command(command_name, stdout=out)
    return JsonResponse({"ok": True, "output": out.getvalue().strip()})


@csrf_exempt
@require_POST
def task_expire_shifts(request):
    return _run_internal_task(request, "expire_shifts")


@csrf_exempt
@require_POST
def task_send_shift_reminders(request):
    return _run_internal_task(request, "send_shift_reminders")
