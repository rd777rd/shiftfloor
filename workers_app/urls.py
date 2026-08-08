from django.urls import path

from . import views

app_name = "workers_app"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("certifications/", views.certification_list, name="certification_list"),
    path(
        "certifications/upload/",
        views.certification_upload,
        name="certification_upload",
    ),
    path("<int:pk>/profile/", views.worker_public_profile, name="worker_public_profile"),
]
