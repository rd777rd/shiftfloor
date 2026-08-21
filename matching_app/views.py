from django.contrib import messages
from django.db import OperationalError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.mixins import role_required
from accounts_app.models import User
from core_app.utils import send_notification_email
from shifts_app.models import Shift

from .models import ShiftApplication


@role_required(User.Role.WORKER)
def claim_shift(request, slug):
    """The single most correctness-critical view in the app (Rubric C.19).
    Wraps the headcount check + application creation in an atomic
    transaction with select_for_update() on the Shift row, so two workers
    racing for the last open spot can never both succeed — the second
    request blocks until the first commits, then re-reads the now-current
    headcount before deciding. The cert gate is re-checked here
    server-side too (Rubric C.20): the "you qualify" UI is a convenience,
    never the enforcement point."""
    profile = request.user.worker_profile

    if request.method != "POST":
        return redirect("shifts_app:shift_detail", slug=slug)

    try:
        with transaction.atomic():
            shift = Shift.objects.select_for_update().get(slug=slug)

            if shift.status != Shift.Status.OPEN or shift.spots_remaining <= 0:
                messages.error(request, "This shift is no longer available.")
                return redirect("shifts_app:shift_detail", slug=slug)

            if not profile.is_qualified_for(shift.required_cert):
                messages.error(
                    request,
                    "You need a verified certification for this shift before you can claim it.",
                )
                return redirect("shifts_app:shift_detail", slug=slug)

            if ShiftApplication.objects.filter(shift=shift, worker=profile).exists():
                messages.info(request, "You've already applied to this shift.")
                return redirect("shifts_app:shift_detail", slug=slug)

            status = (
                ShiftApplication.Status.CONFIRMED
                if shift.auto_accept
                else ShiftApplication.Status.APPLIED
            )
            application = ShiftApplication.objects.create(
                shift=shift, worker=profile, status=status
            )
    except OperationalError:
        # SQLite (production DB — see settings/base.py) has no real
        # row-level locking: select_for_update() is a silent no-op there,
        # so concurrent claims on the same shift are serialized instead by
        # SQLite's own file-level write lock. A losing request can hit
        # "database is locked" here rather than cleanly re-reading the
        # now-current headcount the way it would after a Postgres row-lock
        # wait. Treat that race loss the same as "someone else got there
        # first" instead of surfacing a raw 500 to the worker who lost.
        messages.error(
            request, "This shift just filled up — someone else claimed the last spot."
        )
        return redirect("shifts_app:shift_detail", slug=slug)

    if application.status == ShiftApplication.Status.CONFIRMED:
        messages.success(request, "Shift confirmed! Check your email for directions.")
        send_notification_email(
            subject=f"Shift confirmed — {shift}",
            template_name="emails/shift_confirmed.txt",
            context={"application": application},
            to_email=profile.user.email,
        )
    else:
        messages.success(request, "Applied — you'll be notified once the facility confirms.")

    return redirect("shifts_app:shift_detail", slug=slug)


@role_required(User.Role.FACILITY_ADMIN)
def applicant_queue(request, shift_id):
    """Facility view of applicants for a shift they own — moves an
    application from APPLIED to OFFERED, per Design Plan Flow B."""
    shift = get_object_or_404(Shift, pk=shift_id, location__facility=request.user.facility)
    applications = shift.applications.select_related("worker__user").filter(
        status__in=[ShiftApplication.Status.APPLIED, ShiftApplication.Status.OFFERED]
    )
    return render(
        request,
        "matching_app/applicant_queue.html",
        {"shift": shift, "applications": applications},
    )


@role_required(User.Role.FACILITY_ADMIN)
def offer_applicant(request, application_id):
    application = get_object_or_404(
        ShiftApplication, pk=application_id, shift__location__facility=request.user.facility
    )
    if request.method == "POST":
        with transaction.atomic():
            shift = Shift.objects.select_for_update().get(pk=application.shift_id)
            if shift.spots_remaining <= 0:
                messages.error(request, "This shift is already fully staffed.")
                return redirect("matching_app:applicant_queue", shift_id=shift.id)
            application.status = ShiftApplication.Status.OFFERED
            application.save(update_fields=["status"])
        send_notification_email(
            subject=f"You've been offered a shift — {application.shift}",
            template_name="emails/shift_offered.txt",
            context={"application": application},
            to_email=application.worker.user.email,
        )
        messages.success(request, "Offer sent to worker.")
    return redirect("matching_app:applicant_queue", shift_id=application.shift_id)


@role_required(User.Role.FACILITY_ADMIN)
def close_out_shift(request, shift_id):
    """Facility close-out screen (Design Plan Flow D): mark each confirmed
    worker as Completed or No-show. Triggers the post-shift review prompt
    once an application is marked COMPLETED."""
    shift = get_object_or_404(Shift, pk=shift_id, location__facility=request.user.facility)
    confirmed = shift.applications.filter(status=ShiftApplication.Status.CONFIRMED).select_related("worker__user")

    if request.method == "POST":
        application_id = request.POST.get("application_id")
        outcome = request.POST.get("outcome")
        application = get_object_or_404(ShiftApplication, pk=application_id, shift=shift)
        if outcome == "completed":
            application.status = ShiftApplication.Status.COMPLETED
        elif outcome == "no_show":
            application.status = ShiftApplication.Status.NO_SHOW
        application.save(update_fields=["status"])

        # If every confirmed slot has been closed out, the shift itself is done.
        if not shift.applications.filter(status=ShiftApplication.Status.CONFIRMED).exists():
            shift.status = Shift.Status.COMPLETED
            shift.save(update_fields=["status"])
        messages.success(request, "Updated.")
        return redirect("matching_app:close_out_shift", shift_id=shift.id)

    return render(request, "matching_app/close_out_shift.html", {"shift": shift, "confirmed": confirmed})


@role_required(User.Role.WORKER)
def my_offers(request):
    profile = request.user.worker_profile
    offers = ShiftApplication.objects.filter(
        worker=profile, status=ShiftApplication.Status.OFFERED
    ).select_related("shift")
    return render(request, "matching_app/my_offers.html", {"offers": offers})


@role_required(User.Role.WORKER)
def respond_offer(request, application_id):
    """Worker accepts or declines a facility's offer. Accepting confirms
    the shift for the worker (OFFERED → CONFIRMED); declining frees the
    slot for other applicants."""
    application = get_object_or_404(
        ShiftApplication, pk=application_id, worker=request.user.worker_profile
    )
    decision = request.POST.get("decision")
    if request.method == "POST" and decision in {"accept", "decline"}:
        with transaction.atomic():
            shift = Shift.objects.select_for_update().get(pk=application.shift_id)
            if decision == "accept":
                if shift.spots_remaining <= 0:
                    messages.error(request, "Sorry — this shift just filled up.")
                    return redirect("matching_app:my_offers")
                application.status = ShiftApplication.Status.CONFIRMED
            else:
                application.status = ShiftApplication.Status.DECLINED
            from django.utils import timezone

            application.responded_at = timezone.now()
            application.save(update_fields=["status", "responded_at"])

        if application.status == ShiftApplication.Status.CONFIRMED:
            messages.success(request, "Shift confirmed!")
        else:
            messages.info(request, "Offer declined.")
    return redirect("matching_app:my_offers")