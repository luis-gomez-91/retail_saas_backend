from django.db import models

from core.models.catalog import Module


class AppPermission(models.Model):
    """Permiso de aplicación con código estable `modulo.recurso.accion`."""

    code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=255)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='permissions',
        null=True,
        blank=True,
        help_text='Nulo = permiso global (no ligado a módulo de plan).',
    )

    class Meta:
        ordering = ['code']
        verbose_name = 'permiso'
        verbose_name_plural = 'permisos'

    def __str__(self) -> str:
        return self.code


class Role(models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    permissions = models.ManyToManyField(
        AppPermission,
        related_name='roles',
        blank=True,
    )

    class Meta:
        ordering = ['code']
        verbose_name = 'rol'
        verbose_name_plural = 'roles'

    def __str__(self) -> str:
        return self.name


class ModuleRole(models.Model):
    """Qué módulos puede operar un rol cuando el plan del tenant los incluye."""

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='module_links')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='role_links')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'module'], name='uniq_module_role'),
        ]
        verbose_name = 'módulo por rol'
        verbose_name_plural = 'módulos por rol'
