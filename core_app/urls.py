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
]
