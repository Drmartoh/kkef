from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from apps.accounts.models import User


def user_can_manage_site(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return getattr(user, "role", None) in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN)


class ManageAccessMixin(LoginRequiredMixin):
    """Forum administrators and Django staff only."""

    login_url = "/accounts/login/?next=/manage/"

    def dispatch(self, request, *args, **kwargs):
        if not user_can_manage_site(request.user):
            raise PermissionDenied("You need forum administrator access to open the control center.")
        return super().dispatch(request, *args, **kwargs)
