from django.urls import path

from . import views

app_name = "facilities_app"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("locations/", views.location_list, name="location_list"),
    path("<slug:slug>/", views.facility_detail, name="facility_detail"),
]
