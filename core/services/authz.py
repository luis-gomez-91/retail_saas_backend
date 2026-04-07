from __future__ import annotations

from django.db.models import QuerySet

from core.models import Empresa, Modulo, Persona, PersonaEmpresa, PlanModulo, RolPersonaEmpresa
from core.services.quotas import get_active_subscription

# Menú fijo superusuario (`Modulo.codigo`); si is_admin, se unen ADMIN_MENU_CODES.
SUPERUSER_MENU_CODES = ('modulos', 'personas', 'planes', 'suscripciones')
ADMIN_MENU_CODES = ('personas', 'roles', 'empresas', 'organizaciones', 'sucursales')


def _assignment_covers_request(
    *,
    assign_org_id: int | None,
    assign_suc_id: int | None,
    request_org_id: int | None,
    request_suc_id: int | None,
) -> bool:
    if assign_org_id is None and assign_suc_id is None:
        return True
    if assign_suc_id is not None:
        return request_suc_id == assign_suc_id
    if request_org_id is None:
        return False
    return request_org_id == assign_org_id


def person_has_module(
    persona: Persona,
    empresa: Empresa,
    modulo_id: int,
    *,
    organizacion_id: int | None = None,
    sucursal_id: int | None = None,
    allow_without_subscription: bool = False,
) -> bool:
    """
    El plan del tenant incluye el módulo (PlanModulo) y algún rol asignado a la persona
    incluye ese módulo, con alcance compatible.
    """
    sub = get_active_subscription(empresa.cuenta_facturacion)
    if not sub and not allow_without_subscription:
        return False

    plan_module_ids: set[int] = set()
    if sub:
        plan_module_ids = set(
            PlanModulo.objects.filter(plan_id=sub.plan_id).values_list('modulo_id', flat=True)
        )

    if sub and modulo_id not in plan_module_ids:
        return False

    try:
        pe = PersonaEmpresa.objects.get(persona=persona, empresa=empresa, activa=True)
    except PersonaEmpresa.DoesNotExist:
        return False

    assignments = RolPersonaEmpresa.objects.filter(persona=persona).select_related('rol')
    for a in assignments:
        if not _assignment_covers_request(
            assign_org_id=None,
            assign_suc_id=None,
            request_org_id=organizacion_id,
            request_suc_id=sucursal_id,
        ):
            continue
        if a.rol.rol_modulos.filter(modulo_id=modulo_id).exists():
            return True
    return False


def _modules_by_codes(codes: tuple[str, ...]) -> QuerySet[Modulo]:
    return Modulo.objects.filter(codigo__in=codes).order_by('codigo')


def list_accessible_modules_for_user(user) -> QuerySet[Modulo]:
    """
    Menú: RBAC ∩ plan por membresía; superusuario → SUPERUSER_MENU_CODES
    (+ ADMIN_MENU_CODES si is_admin); is_admin suma ADMIN al RBAC.
    """
    if not user or not user.is_authenticated:
        return Modulo.objects.none()

    if getattr(user, 'is_superuser', False):
        codes = set(SUPERUSER_MENU_CODES)
        if getattr(user, 'is_admin', False):
            codes |= set(ADMIN_MENU_CODES)
        return _modules_by_codes(tuple(sorted(codes)))

    try:
        persona = user.persona
    except Persona.DoesNotExist:
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
            return Modulo.objects.all().order_by('codigo')
        if getattr(user, 'is_admin', False):
            return _modules_by_codes(ADMIN_MENU_CODES)
        return Modulo.objects.none()

    memberships = PersonaEmpresa.objects.filter(persona=persona, activa=True).select_related(
        'empresa',
        'empresa__cuenta_facturacion',
    )

    module_ids: set[int] = set()
    if memberships:
        for pe in memberships:
            empresa = pe.empresa
            sub = get_active_subscription(empresa.cuenta_facturacion)
            if not sub:
                continue
            plan_mod_ids = set(
                PlanModulo.objects.filter(plan_id=sub.plan_id).values_list('modulo_id', flat=True)
            )
            assignments = RolPersonaEmpresa.objects.filter(persona=persona).prefetch_related(
                'rol__rol_modulos__modulo'
            )
            for a in assignments:
                for rm in a.rol.rol_modulos.all():
                    if rm.modulo_id in plan_mod_ids:
                        module_ids.add(rm.modulo_id)

    if getattr(user, 'is_admin', False):
        module_ids.update(
            Modulo.objects.filter(codigo__in=ADMIN_MENU_CODES).values_list('id', flat=True)
        )

    if not module_ids:
        return Modulo.objects.none()
    return Modulo.objects.filter(id__in=module_ids).order_by('codigo')
