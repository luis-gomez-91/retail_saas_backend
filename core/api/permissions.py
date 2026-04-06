from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """GET permitido a autenticados; escritura solo staff."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsStaffMember(permissions.BasePermission):
    """Staff (`is_staff`) sin exigir `is_superuser`."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class PersonObjectPermission(permissions.BasePermission):
    """Staff o el propio usuario dueño de la Person."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user_id == request.user.pk
