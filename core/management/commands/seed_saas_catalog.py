from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    CuentaFacturacion,
    Empresa,
    EstadoSuscripcion,
    Modulo,
    Persona,
    PersonaEmpresa,
    Plan,
    PlanModulo,
    RolEmpresa,
    RolPersonaEmpresa,
    Suscripcion,
)

Usuario = get_user_model()


class Command(BaseCommand):
    help = (
        'Crea catálogo inicial: módulos, planes (3 niveles), roles con módulos de ejemplo y '
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
        for codigo, nombre, orden in [
            ('trialing', 'En prueba', 0),
            ('active', 'Activa', 1),
            ('past_due', 'Pago vencido', 2),
            ('canceled', 'Cancelada', 3),
            ('paused', 'Pausada', 4),
        ]:
            EstadoSuscripcion.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'orden': orden},
            )

        modules_data = [
            ('dashboard', 'Dashboard', 'Inicio, KPIs y accesos rápidos', 'LayoutDashboard'),
            ('productos', 'Productos', 'Catálogo, stock y precios', 'Package'),
            ('ventas', 'Ventas', 'POS, tickets y cobros', 'ShoppingCart'),
            ('reportes', 'Reportes', 'Informes y exportaciones', 'BarChart3'),
            ('modulos', 'Módulos', 'Catálogo de módulos del producto', 'Boxes'),
            ('personas', 'Personas', 'Usuarios y fichas de persona', 'Users'),
            ('planes', 'Planes', 'Planes comerciales', 'Layers'),
            ('suscripciones', 'Suscripciones', 'Suscripciones y estado de facturación', 'WalletCards'),
            ('roles', 'Roles', 'Roles y permisos por módulo', 'Shield'),
            ('empresas', 'Empresas', 'Empresas (tenants)', 'Building2'),
            ('organizaciones', 'Organizaciones', 'Organizaciones por empresa', 'Network'),
            ('sucursales', 'Sucursales', 'Sucursales y puntos de venta', 'Store'),
        ]
        modules = {}
        for codigo, nombre, desc, icono in modules_data:
            m, _ = Modulo.objects.update_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'descripcion': desc, 'icono': icono},
            )
            modules[codigo] = m

        plans_data = [
            ('basico', 'Básico', 1, 2, 5, ['dashboard', 'productos', 'ventas']),
            ('pro', 'Pro', 3, 10, 50, ['dashboard', 'productos', 'ventas', 'reportes']),
            (
                'enterprise',
                'Enterprise',
                None,
                None,
                None,
                [
                    'dashboard',
                    'productos',
                    'ventas',
                    'reportes',
                    'modulos',
                    'personas',
                    'planes',
                    'suscripciones',
                    'roles',
                    'empresas',
                    'organizaciones',
                    'sucursales',
                ],
            ),
        ]
        plans = {}
        for codigo, nombre, max_e, max_o, max_s, mod_codes in plans_data:
            plan, _ = Plan.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'publico': True,
                    'max_empresas': max_e,
                    'max_organizaciones': max_o,
                    'max_sucursales': max_s,
                },
            )
            plans[codigo] = plan
            PlanModulo.objects.filter(plan=plan).delete()
            for mc in mod_codes:
                PlanModulo.objects.get_or_create(plan=plan, modulo=modules[mc])

        role_admin, _ = RolEmpresa.objects.update_or_create(
            codigo='admin-empresa',
            defaults={'nombre': 'Administrador de empresa'},
        )
        role_admin.establecer_modulos(
            [
                modules['dashboard'],
                modules['productos'],
                modules['ventas'],
                modules['reportes'],
            ]
        )

        role_cajero, _ = RolEmpresa.objects.update_or_create(
            codigo='cajero',
            defaults={'nombre': 'Cajero'},
        )
        role_cajero.establecer_modulos([modules['dashboard'], modules['ventas']])

        self.stdout.write(self.style.SUCCESS('Catálogo SaaS sembrado correctamente.'))

        if options['with_demo']:
            self._seed_demo(plans['pro'], options['demo_username'])

    def _seed_demo(self, plan: Plan, demo_username: str) -> None:
        cf, _ = CuentaFacturacion.objects.get_or_create(nombre='Demo Billing')
        sub = (
            cf.suscripciones.filter(estado__codigo__in=('active', 'trialing'))
            .first()
        )
        if not sub:
            active_status = EstadoSuscripcion.objects.get(codigo='active')
            sub = Suscripcion.objects.create(
                cuenta_facturacion=cf,
                plan=plan,
                estado=active_status,
            )
        user, created = Usuario.objects.get_or_create(
            username=demo_username,
            defaults={
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            user.set_password('demo1234')
            user.save()
        persona, _ = Persona.objects.update_or_create(
            usuario=user,
            defaults={
                'nombre': 'Admin',
                'apellido_paterno': 'Demo',
                'apellido_materno': '',
                'correo_personal': '',
                'telefono': '',
            },
        )
        try:
            empresa = Empresa.objects.get(cuenta_facturacion=cf, slug='demo')
        except Empresa.DoesNotExist:
            empresa = Empresa(
                cuenta_facturacion=cf,
                slug='demo',
                nombre='Empresa Demo',
            )
            empresa.save(skip_quota_check=True)
        PersonaEmpresa.objects.get_or_create(
            persona=persona,
            empresa=empresa,
            defaults={'activa': True},
        )
        admin_role = RolEmpresa.objects.get(codigo='admin-empresa')
        RolPersonaEmpresa.objects.get_or_create(
            persona=persona,
            rol=admin_role,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Demo: cuenta "{cf.nombre}", plan {plan.codigo}, empresa "{empresa.slug}", '
                f'usuario {demo_username} / demo1234'
            )
        )
