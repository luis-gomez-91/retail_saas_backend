from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import (
    AppPermission,
    AuthProvider,
    BillingAccount,
    Empresa,
    Module,
    ModuleRole,
    Organizacion,
    Person,
    PersonEmpresa,
    PersonRoleAssignment,
    Plan,
    PlanModule,
    Role,
    Subscription,
    SubscriptionStatus,
    Sucursal,
    User,
    UserIdentity,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('username',)
    list_display = ('username', 'is_staff', 'is_superuser', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username',)
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'is_staff', 'is_superuser'),
            },
        ),
    )


@admin.register(AuthProvider)
class AuthProviderAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('code', 'name')
    ordering = ('sort_order', 'code')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')
    search_fields = ('user__username', 'phone', 'name', 'last_name')


@admin.register(UserIdentity)
class UserIdentityAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_uid', 'is_primary', 'created_at')
    list_filter = ('provider', 'is_primary')
    autocomplete_fields = ('user', 'provider')


class PlanModuleInline(admin.TabularInline):
    model = PlanModule
    extra = 0
    autocomplete_fields = ('module',)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'max_empresas',
        'max_organizaciones',
        'max_sucursales',
        'is_public',
        'display_order',
    )
    list_editable = ('display_order', 'is_public')
    search_fields = ('name', 'code')
    inlines = [PlanModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'module')
    list_filter = ('module',)
    search_fields = ('code', 'name')
    autocomplete_fields = ('module',)


class ModuleRoleInline(admin.TabularInline):
    model = ModuleRole
    extra = 0
    autocomplete_fields = ('module',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    filter_horizontal = ('permissions',)
    inlines = [ModuleRoleInline]


@admin.register(SubscriptionStatus)
class SubscriptionStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('code', 'name')
    ordering = ('sort_order', 'code')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('billing_account', 'plan', 'status', 'current_period_end', 'created_at')
    list_filter = ('status', 'plan')
    autocomplete_fields = ('billing_account', 'plan', 'status')


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    autocomplete_fields = ('plan',)


class EmpresaInline(admin.TabularInline):
    model = Empresa
    extra = 0
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BillingAccount)
class BillingAccountAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [SubscriptionInline, EmpresaInline]


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'billing_account')
    search_fields = ('name', 'slug')
    autocomplete_fields = ('billing_account',)
    prepopulated_fields = {'slug': ('name',)}


class SucursalInline(admin.TabularInline):
    model = Sucursal
    extra = 0


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('name', 'empresa')
    search_fields = ('name',)
    autocomplete_fields = ('empresa',)
    inlines = [SucursalInline]


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizacion')
    search_fields = ('name',)
    autocomplete_fields = ('organizacion',)


@admin.register(PersonEmpresa)
class PersonEmpresaAdmin(admin.ModelAdmin):
    list_display = ('person', 'empresa', 'is_active', 'joined_at')
    list_filter = ('is_active',)
    autocomplete_fields = ('person', 'empresa')


@admin.register(PersonRoleAssignment)
class PersonRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ('person', 'role', 'empresa', 'organizacion', 'sucursal')
    autocomplete_fields = ('person', 'role', 'empresa', 'organizacion', 'sucursal')
