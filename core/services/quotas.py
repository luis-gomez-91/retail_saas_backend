from __future__ import annotations

from typing import Optional

from django.db.models import Count

from core.exceptions import PlanLimitExceeded
from core.models import BillingAccount, Empresa, Plan, Subscription, Sucursal

_ACTIVE_SUBSCRIPTION_STATUS_CODES = ('trialing', 'active')


def get_active_subscription(billing_account: BillingAccount) -> Optional[Subscription]:
    return (
        billing_account.subscriptions.filter(
            status__code__in=_ACTIVE_SUBSCRIPTION_STATUS_CODES,
        )
        .select_related('plan', 'status')
        .order_by('-created_at')
        .first()
    )


def get_active_plan_for_empresa(empresa: Empresa) -> Optional[Plan]:
    sub = get_active_subscription(empresa.billing_account)
    return sub.plan if sub else None


def _limit_reached(current: int, maximum: int | None) -> bool:
    if maximum is None:
        return False
    return current >= maximum


def assert_can_create_empresa(billing_account: BillingAccount) -> None:
    sub = get_active_subscription(billing_account)
    if not sub:
        raise PlanLimitExceeded(
            'No hay suscripción activa para esta cuenta.',
            code='no_subscription',
        )
    plan = sub.plan
    count = billing_account.empresas.count()
    if _limit_reached(count, plan.max_empresas):
        raise PlanLimitExceeded(
            f'Máximo de empresas para el plan ({plan.max_empresas}) alcanzado.',
            code='max_empresas',
        )


def assert_can_create_organizacion(empresa: Empresa) -> None:
    sub = get_active_subscription(empresa.billing_account)
    if not sub:
        raise PlanLimitExceeded(
            'No hay suscripción activa para esta cuenta.',
            code='no_subscription',
        )
    plan = sub.plan
    count = empresa.organizaciones.count()
    if _limit_reached(count, plan.max_organizaciones):
        raise PlanLimitExceeded(
            f'Máximo de organizaciones para el plan ({plan.max_organizaciones}) alcanzado.',
            code='max_organizaciones',
        )


def assert_can_create_sucursal(empresa: Empresa) -> None:
    sub = get_active_subscription(empresa.billing_account)
    if not sub:
        raise PlanLimitExceeded(
            'No hay suscripción activa para esta cuenta.',
            code='no_subscription',
        )
    plan = sub.plan
    count = (
        Sucursal.objects.filter(organizacion__empresa=empresa).aggregate(n=Count('id'))['n'] or 0
    )
    if _limit_reached(count, plan.max_sucursales):
        raise PlanLimitExceeded(
            f'Máximo de sucursales para el plan ({plan.max_sucursales}) alcanzado.',
            code='max_sucursales',
        )
