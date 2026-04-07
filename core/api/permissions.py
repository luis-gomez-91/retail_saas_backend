from rest_framework import permissions


def is_staff_or_superuser(user) -> bool:
    """Staff o superusuario: privilegio amplio en la API."""
    return bool(
        user
        and user.is_authenticated
        and (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))
    )


def is_staff_super_or_admin(user) -> bool:
    """Incluye operadores con `is_admin`."""
    return is_staff_or_superuser(user) or bool(
        user and user.is_authenticated and getattr(user, 'is_admin', False)
    )


class IsStaffOrReadOnly(permissions.BasePermission):
    """GET permitido a autenticados; escritura equipo / super / administrador."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_staff_super_or_admin(request.user)


class IsStaffMember(permissions.BasePermission):
    """Escritura restringida a staff, superusuario o is_admin."""

    def has_permission(self, request, view):
        return is_staff_super_or_admin(request.user)


class PersonaObjectPermission(permissions.BasePermission):
    """Equipo/super/admin o el usuario dueño de la Persona."""

    def has_object_permission(self, request, view, obj):
        if is_staff_super_or_admin(request.user):
            return True
        return obj.usuario_id == request.user.pk
