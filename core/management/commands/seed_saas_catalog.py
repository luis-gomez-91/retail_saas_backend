from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
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
    PlanModule,
    Role,
    Subscription,
    SubscriptionStatus,
    UserIdentity,
)

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Crea catálogo inicial: módulos, planes (3 niveles), permisos de ejemplo y '
        'una cuenta demo opcional.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-demo',
            action='store_true',
            help='Crea cuenta de facturación, suscripción activa y empresa demo.',
        )
        parser.add_argument(
            '--demo-username',
            default='demo_admin',
            help='Nombre de usuario del admin demo (solo con --with-demo).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        for code, name, order in [
            ('password', 'Contraseña', 0),
            ('google', 'Google', 1),
            ('microsoft', 'Microsoft', 2),
            ('oidc', 'OpenID Connect', 3),
            ('saml', 'SAML', 4),
        ]:
            AuthProvider.objects.get_or_create(
                code=code,
                defaults={'name': name, 'sort_order': order},
            )
        for code, name, order in [
            ('trialing', 'En prueba', 0),
            ('active', 'Activa', 1),
            ('past_due', 'Pago vencido', 2),
            ('canceled', 'Cancelada', 3),
            ('paused', 'Pausada', 4),
        ]:
            SubscriptionStatus.objects.get_or_create(
                code=code,
                defaults={'name': name, 'sort_order': order},
            )

        modules_data = [
            ('core', 'Core', 'Administración y ajustes base'),
            ('inventario', 'Inventario', 'Stock y productos'),
            ('rrhh', 'RRHH', 'Empleados y nómina'),
        ]
        modules = {}
        for code, name, desc in modules_data:
            m, _ = Module.objects.update_or_create(
                code=code,
                defaults={'name': name, 'description': desc},
            )
            modules[code] = m

        plans_data = [
            ('basico', 'Básico', 1, 2, 5, ['core', 'inventario']),
            ('pro', 'Pro', 3, 10, 50, ['core', 'inventario', 'rrhh']),
            ('enterprise', 'Enterprise', None, None, None, ['core', 'inventario', 'rrhh']),
        ]
        plans = {}
        for code, name, max_e, max_o, max_s, mod_codes in plans_data:
            plan, _ = Plan.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'is_public': True,
                    'max_empresas': max_e,
                    'max_organizaciones': max_o,
                    'max_sucursales': max_s,
                },
            )
            plans[code] = plan
            PlanModule.objects.filter(plan=plan).delete()
            for mc in mod_codes:
                PlanModule.objects.get_or_create(plan=plan, module=modules[mc])

        perms_data = [
            ('inventario.producto.view', 'Ver productos', 'inventario'),
            ('inventario.producto.edit', 'Editar productos', 'inventario'),
            ('rrhh.empleado.view', 'Ver empleados', 'rrhh'),
            ('rrhh.empleado.edit', 'Editar empleados', 'rrhh'),
        ]
        perms = {}
        for code, name, mod_code in perms_data:
            p, _ = AppPermission.objects.update_or_create(
                code=code,
                defaults={'name': name, 'module': modules[mod_code]},
            )
            perms[code] = p

        role_admin, _ = Role.objects.update_or_create(
            code='admin-empresa',
            defaults={'name': 'Administrador de empresa'},
        )
        role_admin.permissions.set(perms.values())
        for mod_code in ['core', 'inventario', 'rrhh']:
            ModuleRole.objects.get_or_create(role=role_admin, module=modules[mod_code])

        role_cajero, _ = Role.objects.update_or_create(
            code='cajero',
            defaults={'name': 'Cajero'},
        )
        role_cajero.permissions.set([perms['inventario.producto.view']])
        ModuleRole.objects.get_or_create(role=role_cajero, module=modules['inventario'])

        self.stdout.write(self.style.SUCCESS('Catálogo SaaS sembrado correctamente.'))

        if options['with_demo']:
            self._seed_demo(plans['pro'], options['demo_username'])

    def _seed_demo(self, plan: Plan, demo_username: str) -> None:
        ba, _ = BillingAccount.objects.get_or_create(name='Demo Billing')
        sub = (
            ba.subscriptions.filter(status__code__in=('active', 'trialing'))
            .first()
        )
        if not sub:
            active_status = SubscriptionStatus.objects.get(code='active')
            sub = Subscription.objects.create(
                billing_account=ba,
                plan=plan,
                status=active_status,
            )
        user, created = User.objects.get_or_create(
            username=demo_username,
            defaults={
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            user.set_password('demo1234')
            user.save()
        person, _ = Person.objects.update_or_create(
            user=user,
            defaults={
                'name': 'Admin',
                'last_name': 'Demo',
                'second_last_name': '',
                'personal_email': '',
                'phone': '',
            },
        )
        pwd_provider = AuthProvider.objects.get(code='password')
        UserIdentity.objects.get_or_create(
            user=user,
            provider=pwd_provider,
            provider_uid='',
            defaults={'is_primary': True},
        )
        empresa, _ = Empresa.objects.get_or_create(
            billing_account=ba,
            slug='demo',
            defaults={'name': 'Empresa Demo'},
        )
        PersonEmpresa.objects.get_or_create(
            person=person,
            empresa=empresa,
            defaults={'is_active': True},
        )
        admin_role = Role.objects.get(code='admin-empresa')
        PersonRoleAssignment.objects.get_or_create(
            person=person,
            role=admin_role,
            empresa=empresa,
            organizacion=None,
            sucursal=None,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Demo: cuenta "{ba.name}", plan {plan.code}, empresa "{empresa.slug}", '
                f'usuario {demo_username} / demo1234'
            )
        )
