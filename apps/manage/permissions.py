from rest_framework import permissions

from apps.accounts.models import User


class IsManageOperator(permissions.BasePermission):
    """Forum administrators and Django staff — full in-dashboard CRUD."""

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if u.is_superuser or u.is_staff:
            return True
        return getattr(u, "role", None) in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN)
