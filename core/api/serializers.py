from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.services.authz import list_accessible_modules_for_user

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
    RolPersonaEmpresa,
    Suscripcion,
    Sucursal,
)

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = (
            'id',
            'username',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_admin',
            'date_joined',
            'last_login',
        )
        read_only_fields = fields


class MeModuloSerializer(serializers.ModelSerializer):
    """Módulo de menú (ruta derivada del `codigo`)."""

    ruta = serializers.SerializerMethodField()

    class Meta:
        model = Modulo
        fields = ('id', 'codigo', 'nombre', 'descripcion', 'icono', 'ruta')

    def get_ruta(self, obj: Modulo) -> str:
        return f'/{obj.codigo}'


class MeUsuarioSerializer(serializers.ModelSerializer):
    """Perfil en /users/me + módulos de menú."""

    modulos = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = (
            'id',
            'username',
            'is_staff',
            'is_superuser',
            'is_admin',
            'date_joined',
            'last_login',
            'modulos',
        )
        read_only_fields = fields

    @extend_schema_field(
        {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'codigo': {'type': 'string'},
                    'nombre': {'type': 'string'},
                    'descripcion': {'type': 'string'},
                    'icono': {'type': 'string'},
                    'ruta': {'type': 'string'},
                },
            },
        }
    )
    def get_modulos(self, usuario):
        qs = list_accessible_modules_for_user(usuario)
        return MeModuloSerializer(qs, many=True).data


class PersonaSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Persona
        fields = (
            'id',
            'usuario',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'correo_personal',
            'telefono',
            'creado_en',
            'actualizado_en',
        )
        read_only_fields = ('id', 'creado_en', 'actualizado_en')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['usuario'].read_only = True


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ('id', 'codigo', 'nombre', 'descripcion', 'icono')


class RolEmpresaSerializer(serializers.ModelSerializer):
    ids_modulos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Modulo.objects.all(),
        required=False,
        write_only=True,
    )
    modulos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RolEmpresa
        fields = ('id', 'codigo', 'nombre', 'modulos', 'ids_modulos')

    def get_modulos(self, obj: RolEmpresa):
        return list(obj.rol_modulos.values_list('modulo_id', flat=True))

    def create(self, validated_data):
        mods = validated_data.pop('ids_modulos', None)
        rol = RolEmpresa.objects.create(**validated_data)
        if mods is not None:
            rol.establecer_modulos(mods)
        return rol

    def update(self, instance, validated_data):
        mods = validated_data.pop('ids_modulos', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if mods is not None:
            instance.establecer_modulos(mods)
        return instance


class PlanModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModulo
        fields = ('id', 'plan', 'modulo')


class PlanSerializer(serializers.ModelSerializer):
    ids_modulos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Plan
        fields = (
            'id',
            'codigo',
            'nombre',
            'publico',
            'orden_presentacion',
            'max_empresas',
            'max_organizaciones',
            'max_sucursales',
            'ids_modulos',
        )

    @extend_schema_field({'type': 'array', 'items': {'type': 'integer'}})
    def get_ids_modulos(self, obj):
        return list(PlanModulo.objects.filter(plan=obj).values_list('modulo_id', flat=True))


class EstadoSuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoSuscripcion
        fields = ('id', 'codigo', 'nombre', 'activo', 'orden')


class CuentaFacturacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaFacturacion
        fields = ('id', 'nombre', 'creado_en')


class SuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = (
            'id',
            'cuenta_facturacion',
            'plan',
            'estado',
            'fin_periodo_actual',
            'id_suscripcion_externa',
            'creado_en',
            'actualizado_en',
        )


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = (
            'id',
            'cuenta_facturacion',
            'nombre',
            'slug',
            'creado_en',
            'actualizado_en',
        )


class OrganizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacion
        fields = ('id', 'empresa', 'nombre', 'creado_en', 'actualizado_en')


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ('id', 'organizacion', 'nombre', 'creado_en', 'actualizado_en')


class PersonaEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaEmpresa
        fields = (
            'id',
            'persona',
            'empresa',
            'activa',
            'invitado_en',
            'ingreso_en',
        )
        read_only_fields = ('ingreso_en',)


class RolPersonaEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPersonaEmpresa
        fields = (
            'id',
            'persona',
            'rol',
        )
