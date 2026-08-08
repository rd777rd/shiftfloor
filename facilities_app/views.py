from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.mixins import role_required
from accounts_app.models import User
from core_app.utils import geocode_address
from shifts_app.models import Shift

from .forms import FacilityLocationForm, FacilityProfileForm
from .models import Facility, FacilityLocation


@role_required(User.Role.FACILITY_ADMIN)
def dashboard(request):
    """Facility home: KPI strip (open shifts, fill rate, upcoming shifts)
    plus shift cards with live applicant counts, per Design Plan §6."""
    facility = request.user.facility
    shifts = Shift.objects.filter(location__facility=facility).select_related("location")
    open_shifts = shifts.filter(status="OPEN")
    upcoming = shifts.exclude(status__in=["CANCELLED", "EXPIRED"]).order_by("start_datetime")[:10]

    return render(
        request,
        "facilities_app/dashboard.html",
        {
            "facility": facility,
            "open_shift_count": open_shifts.count(),
            "fill_rate": facility.fill_rate(),
            "upcoming_shifts": upcoming,
        },
    )


@login_required
def profile_edit(request):
    facility = get_object_or_404(Facility, user=request.user)
    if request.method == "POST":
        form = FacilityProfileForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Facility profile updated.")
            return redirect("facilities_app:profile_edit")
    else:
        form = FacilityProfileForm(instance=facility)
    return render(request, "facilities_app/profile_form.html", {"form": form})


@role_required(User.Role.FACILITY_ADMIN)
def location_list(request):
    facility = request.user.facility
    if request.method == "POST":
        form = FacilityLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.facility = facility
            location.lat, location.lng = geocode_address(form.cleaned_data["address"])
            location.save()
            messages.success(request, "Location added.")
            return redirect("facilities_app:location_list")
    else:
        form = FacilityLocationForm()
    return render(
        request,
        "facilities_app/location_list.html",
        {"locations": facility.locations.all(), "form": form},
    )


def facility_detail(request, slug):
    """Public facility profile — doubles as a local SEO landing page per
    SEO Plan §3."""
    facility = get_object_or_404(Facility, slug=slug, verified=True)
    open_shifts = Shift.objects.filter(location__facility=facility, status="OPEN")
    return render(
        request,
        "facilities_app/facility_detail.html",
        {"facility": facility, "open_shifts": open_shifts},
    )
