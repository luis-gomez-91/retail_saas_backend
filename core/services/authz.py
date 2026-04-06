from __future__ import annotations

from core.models import (
    AppPermission,
    Empresa,
    ModuleRole,
    Person,
    PersonRoleAssignment,
    PlanModule,
)
from core.services.quotas import get_active_subscription


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


def person_has_permission(
    person: Person,
    empresa: Empresa,
    permission_code: str,
    *,
    organizacion_id: int | None = None,
    sucursal_id: int | None = None,
    allow_without_subscription: bool = False,
) -> bool:
    """
    Plan (módulos vía PlanModule) + ModuleRole + permisos del rol + alcance.
    Si el permiso no tiene módulo, no aplica gateo por plan.
    """
    try:
        perm = AppPermission.objects.select_related('module').get(code=permission_code)
    except AppPermission.DoesNotExist:
        return False

    sub = get_active_subscription(empresa.billing_account)
    if not sub and not allow_without_subscription:
        return False

    plan_module_ids: set[int] = set()
    if sub:
        plan_module_ids = set(
            PlanModule.objects.filter(plan_id=sub.plan_id).values_list('module_id', flat=True)
        )

    if perm.module_id and sub and perm.module_id not in plan_module_ids:
        return False

    assignments = PersonRoleAssignment.objects.filter(person=person, empresa=empresa).select_related(
        'role',
    )
    for a in assignments:
        if not _assignment_covers_request(
            assign_org_id=a.organizacion_id,
            assign_suc_id=a.sucursal_id,
            request_org_id=organizacion_id,
            request_suc_id=sucursal_id,
        ):
            continue
        role = a.role
        if not role.permissions.filter(pk=perm.pk).exists():
            continue
        if perm.module_id:
            if not ModuleRole.objects.filter(role_id=role.id, module_id=perm.module_id).exists():
                continue
        return True
    return False
