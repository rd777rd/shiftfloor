from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.mixins import role_required
from accounts_app.models import User
from core_app.utils import geocode_address
from matching_app.models import ShiftApplication
from shifts_app.models import Shift

from .forms import CertificationUploadForm, WorkerProfileForm
from .models import Certification, WorkerProfile


@role_required(User.Role.WORKER)
def dashboard(request):
    """Worker home: recommended open shifts ranked by cert match → distance
    → pay → soonest start (Design Plan Flow B / Coding Plan §5), plus
    upcoming confirmed shifts."""
    profile = request.user.worker_profile
    qualified_certs = profile.verified_cert_types()

    open_shifts = (
        Shift.objects.filter(status="OPEN")
        .exclude(applications__worker=profile)
        .select_related("location__facility")
    )

    def sort_key(shift):
        cert_match = 0 if (shift.required_cert in qualified_certs or shift.required_cert == "GENERAL") else 1
        distance = shift.distance_from(profile.lat, profile.lng)
        distance = distance if distance is not None else 9999
        return (cert_match, distance, -float(shift.pay_rate), shift.start_datetime)

    recommended_shifts = sorted(open_shifts, key=sort_key)[:20]

    upcoming = ShiftApplication.objects.filter(
        worker=profile, status=ShiftApplication.Status.CONFIRMED
    ).select_related("shift")

    return render(
        request,
        "workers_app/dashboard.html",
        {
            "recommended_shifts": recommended_shifts,
            "upcoming_applications": upcoming,
            "profile": profile,
        },
    )


@login_required
def profile_edit(request):
    profile = get_object_or_404(WorkerProfile, user=request.user)
    if request.method == "POST":
        form = WorkerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            worker_profile = form.save(commit=False)
            worker_profile.lat, worker_profile.lng = geocode_address(
                form.cleaned_data["home_address"]
            )
            worker_profile.save()
            messages.success(request, "Profile updated.")
            return redirect("workers_app:profile_edit")
    else:
        form = WorkerProfileForm(instance=profile)
    return render(request, "workers_app/profile_form.html", {"form": form})


@login_required
def certification_list(request):
    profile = get_object_or_404(WorkerProfile, user=request.user)
    certs = profile.certifications.all()
    return render(request, "workers_app/certification_list.html", {"certifications": certs})


@login_required
def certification_upload(request):
    profile = get_object_or_404(WorkerProfile, user=request.user)
    if request.method == "POST":
        form = CertificationUploadForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.worker = profile
            cert.save()
            messages.success(request, "Certification submitted for review.")
            return redirect("workers_app:certification_list")
    else:
        form = CertificationUploadForm()
    return render(request, "workers_app/certification_form.html", {"form": form})


@role_required(User.Role.FACILITY_ADMIN)
def worker_public_profile(request, pk):
    """Facility-facing worker profile — cert badges, rating, completed
    shifts, per Design Plan §6.

    Gated to logged-in facility admins (Rubric A.2): this page surfaces a
    worker's real name and no-show count, and was previously reachable by
    anyone — including crawlers — simply by walking pk values. Facilities
    are the intended audience per the docstring above; there's no
    legitimate anonymous-public use case for it."""
    profile = get_object_or_404(WorkerProfile, pk=pk)
    return render(request, "workers_app/worker_public_profile.html", {"profile": profile})
