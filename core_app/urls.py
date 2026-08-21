from django.urls import path

from . import views

app_name = "core_app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("how-it-works/", views.HowItWorksView.as_view(), name="how_it_works"),
    path(
        "certifications/",
        views.CertificationsInfoView.as_view(),
        name="certifications_info",
    ),
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("go/", views.role_redirect, name="role_redirect"),
    # Scheduled-task endpoints (called by .github/workflows/scheduled_tasks.yml,
    # shared-secret protected — see core_app.views._run_internal_task)
    path("internal/tasks/expire-shifts/", views.task_expire_shifts, name="task_expire_shifts"),
    path(
        "internal/tasks/send-shift-reminders/",
        views.task_send_shift_reminders,
        name="task_send_shift_reminders",
    ),
]
