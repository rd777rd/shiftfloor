"""
Role-based access control shared across facilities_app, workers_app, and
matching_app views. Server-side enforcement only — never trust a template
conditional alone to hide a link, per Coding Plan §4 and Rubric E.36.
"""
from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Class-based view mixin. Set `required_role` to one of
    User.Role.WORKER / User.Role.FACILITY_ADMIN on the subclass."""

    required_role = None

    def test_func(self):
        if self.required_role is None:
            return True
        return self.request.user.role == self.required_role


def role_required(role):
    """Function-based view decorator equivalent of RoleRequiredMixin, used
    for the transactional views (shift claim, offer accept/decline) that
    are implemented as plain functions per Coding Plan §6."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(request.get_full_path())
            if request.user.role != role:
                raise PermissionDenied("You don't have access to this page.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
