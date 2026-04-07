import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Persona

Usuario = get_user_model()


class Command(BaseCommand):
    help = (
        'Entorno local: crea (o actualiza) un único usuario Django `admin` y su registro `Persona` '
        'asociado. No carga catálogo ni tenancy.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='Vuelve a fijar la contraseña en "admin" aunque el usuario ya exista (solo dev).',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and os.environ.get('ALLOW_BOOTSTRAP') != '1':
            raise CommandError(
                'bootstrap_dev está desactivado fuera de DEBUG. '
                'En producción no debe usarse; para forzar (riesgoso): ALLOW_BOOTSTRAP=1'
            )

        with transaction.atomic():
            usr, created = Usuario.objects.get_or_create(
                username='admin',
                defaults={
                    'is_staff': True,
                    'is_superuser': True,
                    'is_admin': True,
                },
            )
            if not created:
                usr.is_staff = True
                usr.is_superuser = True
                usr.is_admin = True
                usr.save(update_fields=['is_staff', 'is_superuser', 'is_admin'])

            if created or options['reset_password']:
                usr.set_password('admin')
                usr.save(update_fields=['password'])

            Persona.objects.update_or_create(
                usuario=usr,
                defaults={
                    'nombre': 'Super',
                    'apellido_paterno': 'Admin',
                    'apellido_materno': '',
                    'correo_personal': 'admin@localhost',
                    'telefono': '',
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                'bootstrap_dev listo: usuario `admin` y persona vinculada '
                '(contraseña `admin` si era nuevo o usaste --reset-password).'
            )
        )
