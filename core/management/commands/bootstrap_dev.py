import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    AppPermission,
    AuthProvider,
    BillingAccount,
    Empresa,
    Module,
    ModuleRole,
    Person,
    PersonEmpresa,
    PersonRoleAssignment,
    Plan,
    Role,
    Subscription,
    SubscriptionStatus,
    UserIdentity,
)

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Entorno local: asegura catálogo (seed), roles superadmin/admin, empresa plataforma '
        'y usuario Django admin / admin con is_superuser y rol superadmin en dominio.'
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
            call_command('seed_saas_catalog', stdout=self.stdout)

            pwd_provider = AuthProvider.objects.get(code='password')
            active_status = SubscriptionStatus.objects.get(code='active')
            enterprise = Plan.objects.get(code='enterprise')

            ba, _ = BillingAccount.objects.get_or_create(
                name='Platform',
                defaults={},
            )
            if not ba.subscriptions.filter(status__code__in=('active', 'trialing')).exists():
                Subscription.objects.create(
                    billing_account=ba,
                    plan=enterprise,
                    status=active_status,
                )

            empresa, _ = Empresa.objects.get_or_create(
                billing_account=ba,
                slug='platform',
                defaults={'name': 'Plataforma'},
            )

            all_modules = list(Module.objects.all())
            all_perms = list(AppPermission.objects.all())

            role_super, _ = Role.objects.update_or_create(
                code='superadmin',
                defaults={'name': 'Super administrador'},
            )
            role_super.permissions.set(all_perms)
            for m in all_modules:
                ModuleRole.objects.get_or_create(role=role_super, module=m)

            admin_domain_perms = list(
                AppPermission.objects.filter(code__in=[
                    'inventario.producto.view',
                    'inventario.producto.edit',
                    'rrhh.empleado.view',
                    'rrhh.empleado.edit',
                ])
            )
            role_admin, _ = Role.objects.update_or_create(
                code='admin',
                defaults={'name': 'Administrador'},
            )
            role_admin.permissions.set(admin_domain_perms)
            for m in all_modules:
                ModuleRole.objects.get_or_create(role=role_admin, module=m)

            user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'is_staff': True,
                    'is_superuser': True,
                },
            )
            if not created:
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['is_staff', 'is_superuser'])

            if created or options['reset_password']:
                user.set_password('admin')
                user.save(update_fields=['password'])

            person, _ = Person.objects.update_or_create(
                user=user,
                defaults={
                    'name': 'Super',
                    'last_name': 'Admin',
                    'second_last_name': '',
                    'personal_email': 'admin@localhost',
                    'phone': '',
                },
            )

            UserIdentity.objects.get_or_create(
                user=user,
                provider=pwd_provider,
                provider_uid='',
                defaults={'is_primary': True},
            )

            PersonEmpresa.objects.get_or_create(
                person=person,
                empresa=empresa,
                defaults={'is_active': True},
            )

            PersonRoleAssignment.objects.get_or_create(
                person=person,
                role=role_super,
                empresa=empresa,
                organizacion=None,
                sucursal=None,
            )

        self.stdout.write(
            self.style.SUCCESS(
                'bootstrap_dev listo. Usuario: admin / admin (si era nuevo o usaste '
                '--reset-password). Empresa dominio: platform. Roles creados: superadmin, admin.'
            )
        )
