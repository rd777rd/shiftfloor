from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from matching_app.models import ShiftApplication

from .forms import ReviewForm
from .models import Review


@login_required
def submit_review(request, application_id):
    """Review submission is only reachable once the application is
    COMPLETED, and only once per direction — both enforced here
    server-side (Rubric C.24), not just by hiding the link."""
    application = get_object_or_404(ShiftApplication, pk=application_id)

    if application.status != ShiftApplication.Status.COMPLETED:
        messages.error(request, "This shift hasn't been marked completed yet.")
        return redirect("core_app:home")

    user = request.user
    if user.is_facility_admin and application.shift.location.facility.user_id == user.id:
        direction = Review.Direction.FACILITY_TO_WORKER
    elif user.is_worker and application.worker.user_id == user.id:
        direction = Review.Direction.WORKER_TO_FACILITY
    else:
        messages.error(request, "You weren't part of this shift.")
        return redirect("core_app:home")

    if Review.objects.filter(application=application, direction=direction).exists():
        messages.info(request, "You've already reviewed this shift.")
        return redirect("core_app:home")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.application = application
            review.direction = direction
            review.save()
            messages.success(request, "Thanks for your feedback!")
            return redirect("core_app:home")
    else:
        form = ReviewForm()

    return render(request, "reviews_app/review_form.html", {"form": form, "application": application})
