from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

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
    UserIdentity,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
        )
        read_only_fields = fields


class MeUserSerializer(serializers.ModelSerializer):
    """Perfil mínimo en /users/me (sin flags sensibles si no quieres — aquí útiles para el front)."""

    class Meta:
        model = User
        fields = ('id', 'username', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
        read_only_fields = fields


class PersonSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Person
        fields = (
            'id',
            'user',
            'name',
            'last_name',
            'second_last_name',
            'personal_email',
            'phone',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['user'].read_only = True


class AuthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthProvider
        fields = ('id', 'code', 'name', 'is_active', 'sort_order')


class UserIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserIdentity
        fields = (
            'id',
            'user',
            'provider',
            'provider_uid',
            'is_primary',
            'metadata',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('id', 'code', 'name', 'description')


class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = ('id', 'code', 'name', 'module')


class RoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AppPermission.objects.all(),
        source='permissions',
        required=False,
        write_only=True,
    )
    permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ('id', 'code', 'name', 'permissions', 'permission_ids')

    def create(self, validated_data):
        perms = validated_data.pop('permissions', None)
        role = Role.objects.create(**validated_data)
        if perms is not None:
            role.permissions.set(perms)
        return role

    def update(self, instance, validated_data):
        perms = validated_data.pop('permissions', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if perms is not None:
            instance.permissions.set(perms)
        return instance


class ModuleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleRole
        fields = ('id', 'role', 'module')


class PlanModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModule
        fields = ('id', 'plan', 'module')


class PlanSerializer(serializers.ModelSerializer):
    module_ids = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Plan
        fields = (
            'id',
            'code',
            'name',
            'is_public',
            'display_order',
            'max_empresas',
            'max_organizaciones',
            'max_sucursales',
            'module_ids',
        )

    @extend_schema_field({'type': 'array', 'items': {'type': 'integer'}})
    def get_module_ids(self, obj):
        return list(obj.modules.values_list('id', flat=True))


class SubscriptionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionStatus
        fields = ('id', 'code', 'name', 'is_active', 'sort_order')


class BillingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAccount
        fields = ('id', 'name', 'created_at')


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            'id',
            'billing_account',
            'plan',
            'status',
            'current_period_end',
            'external_subscription_id',
            'created_at',
            'updated_at',
        )


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = (
            'id',
            'billing_account',
            'name',
            'slug',
            'created_at',
            'updated_at',
        )


class OrganizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacion
        fields = ('id', 'empresa', 'name', 'created_at', 'updated_at')


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ('id', 'organizacion', 'name', 'created_at', 'updated_at')


class PersonEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonEmpresa
        fields = (
            'id',
            'person',
            'empresa',
            'is_active',
            'invited_at',
            'joined_at',
        )
        read_only_fields = ('joined_at',)


class PersonRoleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonRoleAssignment
        fields = (
            'id',
            'person',
            'role',
            'empresa',
            'organizacion',
            'sucursal',
        )
