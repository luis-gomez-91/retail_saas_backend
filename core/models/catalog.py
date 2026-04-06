from django.db import models


class Module(models.Model):
    """Módulo funcional del producto (catálogo estable por `code`)."""

    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self) -> str:
        return f'{self.code}'
