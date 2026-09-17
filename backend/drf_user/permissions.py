"""Account object permissions."""

from rest_framework import permissions


class IsTargetUser(permissions.BasePermission):
    """Allow the authenticated owner to modify an account."""

    def has_object_permission(self, request, view, obj):
        """Compare the target account to the authenticated caller."""
        return request.user.is_authenticated and obj.pk == request.user.pk


class IsSuperUser(permissions.BasePermission):
    """Allow administrators to manage account objects."""

    def has_object_permission(self, request, view, obj):
        """Require an authenticated superuser."""
        return request.user.is_authenticated and request.user.is_superuser
