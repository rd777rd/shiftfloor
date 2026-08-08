from django.urls import path

from . import views

app_name = "matching_app"

urlpatterns = [
    path("claim/<slug:slug>/", views.claim_shift, name="claim_shift"),
    path("applicants/<int:shift_id>/", views.applicant_queue, name="applicant_queue"),
    path("close-out/<int:shift_id>/", views.close_out_shift, name="close_out_shift"),
    path("offer/<int:application_id>/", views.offer_applicant, name="offer_applicant"),
    path("offers/", views.my_offers, name="my_offers"),
    path("offers/<int:application_id>/respond/", views.respond_offer, name="respond_offer"),
]
