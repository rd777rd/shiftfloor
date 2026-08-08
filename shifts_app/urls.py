from django.urls import path

from . import views

app_name = "shifts_app"

urlpatterns = [
    path("browse/", views.shift_browse, name="shift_browse"),
    path("post/", views.shift_post, name="shift_post"),
    path("<slug:slug>/", views.shift_detail, name="shift_detail"),
    path("<slug:slug>/edit/", views.shift_edit, name="shift_edit"),
    path("<slug:slug>/cancel/", views.shift_cancel, name="shift_cancel"),
]
