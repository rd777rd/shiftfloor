from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledAuthenticationForm, StyledPasswordResetForm, StyledSetPasswordForm

app_name = "accounts_app"

urlpatterns = [
    path("signup/worker/", views.WorkerSignupView.as_view(), name="signup_worker"),
    path(
        "signup/facility/", views.FacilitySignupView.as_view(), name="signup_facility"
    ),
    # Built-in Django auth views — only templates are customized, not the
    # view logic, per the "use built-in unless absolutely necessary" rule.
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts_app/login.html", form_class=StyledAuthenticationForm
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts_app/password_reset.html",
            form_class=StyledPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts_app/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts_app/password_reset_confirm.html",
            form_class=StyledSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts_app/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("profile/", views.profile, name="profile"),
]
