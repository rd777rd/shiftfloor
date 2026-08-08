from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.mixins import role_required
from accounts_app.models import User

from .forms import ShiftFilterForm, ShiftForm
from .models import Shift


def shift_browse(request):
    """Worker-facing browse/filter view. If the visitor is an authenticated
    worker, results are ranked cert-match → distance → pay → soonest start
    (Design Plan Flow B); anonymous visitors get a simple soonest-first
    list so the page still indexes well for SEO."""
    shifts = Shift.objects.filter(status="OPEN").select_related("location__facility")
    filter_form = ShiftFilterForm(request.GET or None)

    if filter_form.is_valid():
        cert_type = filter_form.cleaned_data.get("cert_type")
        min_pay = filter_form.cleaned_data.get("min_pay")
        if cert_type:
            shifts = shifts.filter(required_cert=cert_type)
        if min_pay:
            shifts = shifts.filter(pay_rate__gte=min_pay)

    profile = getattr(request.user, "worker_profile", None) if request.user.is_authenticated else None
    if profile:
        qualified = profile.verified_cert_types()
        max_distance = filter_form.cleaned_data.get("max_distance") if filter_form.is_valid() else None

        def sort_key(shift):
            cert_match = 0 if (shift.required_cert in qualified or shift.required_cert == "GENERAL") else 1
            distance = shift.distance_from(profile.lat, profile.lng)
            return (cert_match, distance if distance is not None else 9999, -float(shift.pay_rate), shift.start_datetime)

        shifts = sorted(shifts, key=sort_key)
        if max_distance:
            shifts = [
                s for s in shifts
                if (s.distance_from(profile.lat, profile.lng) or 0) <= max_distance
            ]
    else:
        shifts = shifts.order_by("start_datetime")

    return render(
        request,
        "shifts_app/shift_browse.html",
        {"shifts": shifts, "filter_form": filter_form, "profile": profile},
    )


def shift_detail(request, slug):
    shift = get_object_or_404(Shift, slug=slug)
    profile = getattr(request.user, "worker_profile", None) if request.user.is_authenticated else None
    qualifies = profile.is_qualified_for(shift.required_cert) if profile else None
    already_applied = False
    if profile:
        already_applied = shift.applications.filter(worker=profile).exists()
    return render(
        request,
        "shifts_app/shift_detail.html",
        {
            "shift": shift,
            "qualifies": qualifies,
            "already_applied": already_applied,
        },
    )


@role_required(User.Role.FACILITY_ADMIN)
def shift_post(request):
    facility = request.user.facility
    if request.method == "POST":
        form = ShiftForm(request.POST, facility=facility)
        if form.is_valid():
            shift = form.save()
            messages.success(request, "Shift posted — it's now live for matching workers.")
            return redirect("shifts_app:shift_detail", slug=shift.slug)
    else:
        form = ShiftForm(facility=facility)
    return render(request, "shifts_app/shift_post.html", {"form": form})


@role_required(User.Role.FACILITY_ADMIN)
def shift_edit(request, slug):
    shift = get_object_or_404(Shift, slug=slug, location__facility=request.user.facility)
    if request.method == "POST":
        form = ShiftForm(request.POST, instance=shift, facility=request.user.facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Shift updated.")
            return redirect("shifts_app:shift_detail", slug=shift.slug)
    else:
        form = ShiftForm(instance=shift, facility=request.user.facility)
    return render(request, "shifts_app/shift_post.html", {"form": form, "editing": True})


@role_required(User.Role.FACILITY_ADMIN)
def shift_cancel(request, slug):
    shift = get_object_or_404(Shift, slug=slug, location__facility=request.user.facility)
    if request.method == "POST":
        shift.status = Shift.Status.CANCELLED
        shift.save(update_fields=["status"])
        messages.info(request, "Shift cancelled.")
        return redirect("facilities_app:dashboard")
    return render(request, "shifts_app/shift_cancel_confirm.html", {"shift": shift})
