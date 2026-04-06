from django.core.exceptions import ValidationError
from django.db import models

from core.models.billing import BillingAccount
from core.models.identity import Person
from core.models.rbac import Role


class Empresa(models.Model):
    billing_account = models.ForeignKey(
        BillingAccount,
        on_delete=models.PROTECT,
        related_name='empresas',
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['billing_account', 'slug'], name='uniq_empresa_slug_per_account'),
        ]
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def save(self, *args, **kwargs):
        if self._state.adding:
            from core.services.quotas import assert_can_create_empresa

            assert_can_create_empresa(self.billing_account)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Organizacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='organizaciones')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'organización'
        verbose_name_plural = 'organizaciones'

    def save(self, *args, **kwargs):
        if self._state.adding:
            from core.services.quotas import assert_can_create_organizacion

            assert_can_create_organizacion(self.empresa)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} ({self.empresa})'


class Sucursal(models.Model):
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='sucursales')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'sucursal'
        verbose_name_plural = 'sucursales'

    def save(self, *args, **kwargs):
        if self._state.adding:
            from core.services.quotas import assert_can_create_sucursal

            assert_can_create_sucursal(self.organizacion.empresa)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} ({self.organizacion})'


class PersonEmpresa(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='empresa_memberships')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='members')
    is_active = models.BooleanField(default=True)
    invited_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['person', 'empresa'], name='uniq_person_empresa'),
        ]
        verbose_name = 'membresía persona-empresa'
        verbose_name_plural = 'membresías persona-empresa'


class PersonRoleAssignment(models.Model):
    """
    Alcance: empresa (toda), organización (sucursal NULL), o sucursal concreta
    (requiere organizacion igual a la de la sucursal).
    """

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='assignments')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='role_assignments')
    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='role_assignments',
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='role_assignments',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'role', 'empresa', 'organizacion', 'sucursal'],
                name='uniq_person_role_scope',
            ),
        ]
        verbose_name = 'asignación de rol'
        verbose_name_plural = 'asignaciones de rol'

    def clean(self) -> None:
        if self.organizacion_id and self.organizacion.empresa_id != self.empresa_id:
            raise ValidationError({'organizacion': 'La organización debe pertenecer a la empresa indicada.'})
        if self.sucursal_id:
            if not self.organizacion_id:
                raise ValidationError({'sucursal': 'La sucursal requiere una organización.'})
            if self.sucursal.organizacion_id != self.organizacion_id:
                raise ValidationError({'sucursal': 'La sucursal debe pertenecer a la organización indicada.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
