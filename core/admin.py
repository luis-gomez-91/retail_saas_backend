from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import (
    CuentaFacturacion,
    Empresa,
    EstadoSuscripcion,
    Modulo,
    Organizacion,
    Persona,
    PersonaEmpresa,
    Plan,
    PlanModulo,
    RolEmpresa,
    RolModulo,
    RolPersonaEmpresa,
    Suscripcion,
    Sucursal,
    Usuario,
)


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    ordering = ('username',)
    list_display = (
        'username',
        'is_staff',
        'is_superuser',
        'is_admin',
        'is_active',
        'last_login',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_admin', 'is_active')
    search_fields = ('username',)
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_admin',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_superuser',
                    'is_admin',
                ),
            },
        ),
    )


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'creado_en')
    search_fields = ('usuario__username', 'telefono', 'nombre', 'apellido_paterno')


class PlanModuloInline(admin.TabularInline):
    model = PlanModulo
    extra = 0
    autocomplete_fields = ('modulo',)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'codigo',
        'max_empresas',
        'max_organizaciones',
        'max_sucursales',
        'publico',
        'orden_presentacion',
    )
    list_editable = ('orden_presentacion', 'publico')
    search_fields = ('nombre', 'codigo')
    inlines = [PlanModuloInline]


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'icono')
    search_fields = ('codigo', 'nombre', 'icono')
    ordering = ('codigo',)


class RolModuloInline(admin.TabularInline):
    model = RolModulo
    extra = 0
    autocomplete_fields = ('modulo',)


@admin.register(RolEmpresa)
class RolEmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')
    inlines = [RolModuloInline]


@admin.register(EstadoSuscripcion)
class EstadoSuscripcionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'orden')
    list_editable = ('activo', 'orden')
    search_fields = ('codigo', 'nombre')
    ordering = ('orden', 'codigo')


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('cuenta_facturacion', 'plan', 'estado', 'fin_periodo_actual', 'creado_en')
    list_filter = ('estado', 'plan')
    autocomplete_fields = ('cuenta_facturacion', 'plan', 'estado')


class SuscripcionInline(admin.TabularInline):
    model = Suscripcion
    extra = 0
    autocomplete_fields = ('plan',)


class EmpresaInline(admin.TabularInline):
    model = Empresa
    extra = 0
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(CuentaFacturacion)
class CuentaFacturacionAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    inlines = [SuscripcionInline, EmpresaInline]


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'cuenta_facturacion')
    search_fields = ('nombre', 'slug')
    autocomplete_fields = ('cuenta_facturacion',)
    prepopulated_fields = {'slug': ('nombre',)}


class SucursalInline(admin.TabularInline):
    model = Sucursal
    extra = 0


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa')
    search_fields = ('nombre',)
    autocomplete_fields = ('empresa',)
    inlines = [SucursalInline]


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organizacion')
    search_fields = ('nombre',)
    autocomplete_fields = ('organizacion',)


@admin.register(PersonaEmpresa)
class PersonaEmpresaAdmin(admin.ModelAdmin):
    list_display = ('persona', 'empresa', 'activa', 'ingreso_en')
    list_filter = ('activa',)
    search_fields = (
        'persona__usuario__username',
        'persona__nombre',
        'persona__apellido_paterno',
        'empresa__nombre',
        'empresa__slug',
    )
    autocomplete_fields = ('persona', 'empresa')


@admin.register(RolPersonaEmpresa)
class RolPersonaEmpresaAdmin(admin.ModelAdmin):
    list_display = ('persona', 'rol')
    autocomplete_fields = ('persona', 'rol')
