from django.urls import path

from . import views

app_name = "reviews_app"

urlpatterns = [
    path("<int:application_id>/review/", views.submit_review, name="submit_review"),
]
