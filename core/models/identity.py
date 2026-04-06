from django.conf import settings
from django.db import models


class AuthProvider(models.Model):
    """Catálogo de proveedores de autenticación (local, OAuth, SAML, etc.)."""

    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'code']
        verbose_name = 'proveedor de autenticación'
        verbose_name_plural = 'proveedores de autenticación'

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='person',
    )
    name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    second_last_name = models.CharField(max_length=100, blank=True)
    personal_email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'persona'
        verbose_name_plural = 'personas'

    def __str__(self) -> str:
        parts = [self.name, self.last_name, self.second_last_name]
        label = ' '.join(p for p in parts if p).strip()
        if label:
            return label
        return self.user.get_username()


class UserIdentity(models.Model):
    """Identidad de login externa o local vinculada al usuario."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='identities',
    )
    provider = models.ForeignKey(
        AuthProvider,
        on_delete=models.PROTECT,
        related_name='user_identities',
    )
    provider_uid = models.CharField(
        max_length=255,
        blank=True,
        help_text='ID único en el proveedor (vacío para password local).',
    )
    is_primary = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'provider__sort_order', 'provider__code']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'provider', 'provider_uid'],
                name='uniq_user_provider_uid',
            ),
        ]
        verbose_name = 'identidad de usuario'
        verbose_name_plural = 'identidades de usuario'

    def __str__(self) -> str:
        return f'{self.user.get_username()} — {self.provider}'
