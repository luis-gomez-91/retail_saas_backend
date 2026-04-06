from django.db import models

from core.models.catalog import Module


class BillingAccount(models.Model):
    """Raíz comercial: agrupa varias empresas bajo la misma facturación / plan."""

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'cuenta de facturación'
        verbose_name_plural = 'cuentas de facturación'

    def __str__(self) -> str:
        return self.name


class Plan(models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    is_public = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    max_empresas = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Máximo de empresas por cuenta de facturación. Vacío = sin límite.',
    )
    max_organizaciones = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Máximo de organizaciones por empresa. Vacío = sin límite.',
    )
    max_sucursales = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Máximo de sucursales por empresa (todas las orgs). Vacío = sin límite.',
    )
    modules = models.ManyToManyField(
        Module,
        through='PlanModule',
        related_name='plans',
    )

    class Meta:
        ordering = ['display_order', 'code']
        verbose_name = 'plan'
        verbose_name_plural = 'planes'

    def __str__(self) -> str:
        return self.name


class PlanModule(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_modules')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='plan_modules')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['plan', 'module'], name='uniq_plan_module'),
        ]
        verbose_name = 'módulo del plan'
        verbose_name_plural = 'módulos del plan'


class SubscriptionStatus(models.Model):
    """Estado comercial de una suscripción (catálogo)."""

    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'code']
        verbose_name = 'estado de suscripción'
        verbose_name_plural = 'estados de suscripción'

    def __str__(self) -> str:
        return self.name


def _default_subscription_status_trialing_pk() -> int:
    obj, _ = SubscriptionStatus.objects.get_or_create(
        code='trialing',
        defaults={'name': 'En prueba', 'sort_order': 0},
    )
    return obj.pk


class Subscription(models.Model):
    billing_account = models.ForeignKey(
        BillingAccount,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.ForeignKey(
        SubscriptionStatus,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        default=_default_subscription_status_trialing_pk,
    )
    current_period_end = models.DateTimeField(null=True, blank=True)
    external_subscription_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'suscripción'
        verbose_name_plural = 'suscripciones'

    def __str__(self) -> str:
        return f'{self.billing_account} — {self.plan} ({self.status})'
