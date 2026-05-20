from rest_framework import permissions

from apps.accounts.models import User


class IsForumAdminOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(
            u
            and u.is_authenticated
            and (
                u.is_superuser
                or getattr(u, "role", None) in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN)
            )
        )


class IsGroupLeaderOrAbove(IsForumAdminOrAbove):
    def has_permission(self, request, view):
        u = request.user
        if super().has_permission(request, view):
            return True
        return bool(u and u.is_authenticated and u.role == User.Roles.GROUP_LEADER)


class IsStakeholder(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == User.Roles.STAKEHOLDER)


class ReadOnlyUnlessPrivileged(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        u = request.user
        return bool(
            u
            and u.is_authenticated
            and getattr(u, "role", None)
            not in (
                User.Roles.MEMBER,
                User.Roles.DONOR,
                User.Roles.STAKEHOLDER,
            )
        )


def user_can_manage_group(user, group) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role in (User.Roles.SUPER_ADMIN, User.Roles.FORUM_ADMIN):
        return True
    return group.leaders.filter(pk=user.pk).exists()
