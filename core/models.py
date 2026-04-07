"""
Modelos de dominio (monolito temporal: un solo módulo hasta reorganizar).
Nombres de clases y campos en español. El modelo de usuario (`Usuario`) sigue la convención en inglés de Django Auth
(`username`, `is_staff`, `is_admin`, `date_joined`, `password`, `last_login`, `is_superuser`, `groups`, `user_permissions`).
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# --- Usuario ---------------------------------------------------------------


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('El nombre de usuario es obligatorio'))
        username = self.normalize_username(username)
        usuario = self.model(username=username, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuario mínimo: los datos de perfil viven en `Persona`.
    Campos de autenticación en inglés (compatible con AbstractBaseUser / PermissionsMixin).
    """

    username = models.CharField(_('username'), max_length=150, unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_admin = models.BooleanField(
        _('administrator'),
        default=False,
        help_text=_('Operador: ve módulos de gestión tenant (personas, roles, empresas, etc.).'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table = 'core_user'  # histórico: el modelo se llamaba User en la primera migración
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self) -> str:
        return self.username


# --- Identidad -------------------------------------------------------------


class Persona(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='persona',
    )
    nombre = models.CharField(max_length=100, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    correo_personal = models.EmailField(max_length=255, blank=True)
    correo = models.EmailField(max_length=255, blank=True)
    telefono = models.CharField(max_length=32, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'persona'
        verbose_name_plural = 'personas'

    def __str__(self) -> str:
        parts = [self.nombre, self.apellido_paterno, self.apellido_materno]
        label = ' '.join(p for p in parts if p).strip()
        if label:
            return label
        return self.usuario.get_username()


# --- Facturación -----------------------------------------------------------


class CuentaFacturacion(models.Model):
    """Raíz comercial: agrupa varias empresas bajo la misma facturación / plan."""

    nombre = models.CharField(max_length=255)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'cuenta de facturación'
        verbose_name_plural = 'cuentas de facturación'

    def __str__(self) -> str:
        return self.nombre


class EstadoSuscripcion(models.Model):
    """Estado comercial de una suscripción (catálogo)."""

    codigo = models.SlugField(max_length=64, unique=True)
    nombre = models.CharField(max_length=128)
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'codigo']
        verbose_name = 'estado de suscripción'
        verbose_name_plural = 'estados de suscripción'

    def __str__(self) -> str:
        return self.nombre


def _pk_estado_suscripcion_trialing() -> int:
    obj, _ = EstadoSuscripcion.objects.get_or_create(
        codigo='trialing',
        defaults={'nombre': 'En prueba', 'orden': 0},
    )
    return obj.pk


# --- Catálogo / RBAC -------------------------------------------------------


class Modulo(models.Model):
    """
    Área funcional del producto (menú / pantalla según el rol).
    `codigo` es estable (slug) para API y front; `nombre` etiqueta visible.
    """

    codigo = models.SlugField(max_length=64, unique=True)
    nombre = models.CharField(max_length=128)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text='Clave del icono en la UI (p. ej. Lucide en PascalCase).',
    )

    class Meta:
        ordering = ['codigo']

    def __str__(self) -> str:
        return f'{self.codigo}'


class Plan(models.Model):
    codigo = models.SlugField(max_length=64, unique=True)
    nombre = models.CharField(max_length=128)
    publico = models.BooleanField(default=True)
    orden_presentacion = models.PositiveSmallIntegerField(default=0)
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

    class Meta:
        ordering = ['orden_presentacion', 'codigo']
        verbose_name = 'plan'
        verbose_name_plural = 'planes'

    def __str__(self) -> str:
        return self.nombre


class PlanModulo(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_modulos')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='plan_modulos')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['plan', 'modulo'], name='uniq_plan_modulo'),
        ]
        verbose_name = 'módulo del plan'
        verbose_name_plural = 'módulos del plan'


class Suscripcion(models.Model):
    cuenta_facturacion = models.ForeignKey(
        CuentaFacturacion,
        on_delete=models.CASCADE,
        related_name='suscripciones',
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='suscripciones')
    estado = models.ForeignKey(
        EstadoSuscripcion,
        on_delete=models.PROTECT,
        related_name='suscripciones',
        default=_pk_estado_suscripcion_trialing,
    )
    fin_periodo_actual = models.DateTimeField(null=True, blank=True)
    id_suscripcion_externa = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'suscripción'
        verbose_name_plural = 'suscripciones'

    def __str__(self) -> str:
        return f'{self.cuenta_facturacion} — {self.plan} ({self.estado})'


class RolEmpresa(models.Model):
    codigo = models.SlugField(max_length=64, unique=True)
    nombre = models.CharField(max_length=128)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'rol por empresa'
        verbose_name_plural = 'roles por empresa'

    def __str__(self) -> str:
        return self.nombre

    def establecer_modulos(self, modulos) -> None:
        """Reemplaza los módulos del rol usando la tabla explícita `RolModulo`."""
        RolModulo.objects.filter(rol=self).delete()
        if not modulos:
            return
        RolModulo.objects.bulk_create([RolModulo(rol=self, modulo=m) for m in modulos])


class RolModulo(models.Model):
    """Enlace explícito rol ↔ módulo (sustituye el antiguo ManyToMany)."""

    rol = models.ForeignKey(RolEmpresa, on_delete=models.CASCADE, related_name='rol_modulos')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='rol_modulos')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rol', 'modulo'], name='uniq_rol_modulo'),
        ]
        verbose_name = 'módulo del rol'
        verbose_name_plural = 'módulos del rol'


# --- Tenancy ---------------------------------------------------------------


class Empresa(models.Model):
    cuenta_facturacion = models.ForeignKey(
        CuentaFacturacion,
        on_delete=models.PROTECT,
        related_name='empresas',
    )
    nombre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=128)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['cuenta_facturacion', 'slug'],
                name='uniq_empresa_slug_per_account',
            ),
        ]
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def save(self, *args, **kwargs):
        skip_quota_check = kwargs.pop('skip_quota_check', False)
        if self._state.adding and not skip_quota_check:
            from core.services.quotas import assert_can_create_empresa

            assert_can_create_empresa(self.cuenta_facturacion)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nombre


class Organizacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='organizaciones')
    nombre = models.CharField(max_length=255)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'organización'
        verbose_name_plural = 'organizaciones'

    def save(self, *args, **kwargs):
        skip_quota_check = kwargs.pop('skip_quota_check', False)
        if self._state.adding and not skip_quota_check:
            from core.services.quotas import assert_can_create_organizacion

            assert_can_create_organizacion(self.empresa)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.nombre} ({self.empresa})'

class Sucursal(models.Model):
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='sucursales')
    nombre = models.CharField(max_length=255)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'sucursal'
        verbose_name_plural = 'sucursales'

    def save(self, *args, **kwargs):
        skip_quota_check = kwargs.pop('skip_quota_check', False)
        if self._state.adding and not skip_quota_check:
            from core.services.quotas import assert_can_create_sucursal

            assert_can_create_sucursal(self.organizacion.empresa)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.nombre} ({self.organizacion})'


class PersonaEmpresa(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='membresias_empresa')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='miembros')
    activa = models.BooleanField(default=True)
    invitado_en = models.DateTimeField(null=True, blank=True)
    ingreso_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['persona', 'empresa'], name='uniq_persona_empresa'),
        ]
        verbose_name = 'membresía persona-empresa'
        verbose_name_plural = 'membresías persona-empresa'

    def __str__(self) -> str:
        return f'{self.persona} @ {self.empresa}'


class RolPersonaEmpresa(models.Model):
    """
    Rol asignado a una persona.
    """

    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='asignaciones_rol_empresa',
    )
    rol = models.ForeignKey(RolEmpresa, on_delete=models.CASCADE, related_name='asignaciones')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['persona', 'rol'],
                name='uniq_persona_rol_alcance',
            ),
        ]
        verbose_name = 'asignación rol persona'
        verbose_name_plural = 'asignaciones rol persona'

    def clean(self) -> None:
        super().clean()
        persona = self.persona
        if persona is not None and not PersonaEmpresa.objects.filter(persona=persona, activa=True).exists():
            raise ValidationError(
                {
                    'persona': _(
                        'No se puede asignar un rol a una persona sin membresía activa.'
                    ),
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        persona = self.persona
        rol = self.rol
        if persona is not None and rol is not None:
            return f'{persona} — {rol}'
        return 'asignación rol persona (nueva)'



__all__ = [
    'CuentaFacturacion',
    'Empresa',
    'EstadoSuscripcion',
    'Modulo',
    'Organizacion',
    'Persona',
    'PersonaEmpresa',
    'Plan',
    'PlanModulo',
    'RolEmpresa',
    'RolModulo',
    'RolPersona',
    'RolPersonaEmpresa',
    'Suscripcion',
    'Sucursal',
    'Usuario',
]

# Compatibilidad con migraciones antiguas que referencian `core.models` directamente.
UserManager = UsuarioManager
_default_subscription_status_trialing_pk = _pk_estado_suscripcion_trialing
