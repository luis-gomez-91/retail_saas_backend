from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, viewsets

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

from core.api import serializers
from core.api.openapi import (
    TAG_CATALOGO,
    TAG_FACTURACION,
    TAG_TENANCY,
    TAG_USUARIOS,
    tag_model_viewset,
    tag_read_only,
)
from core.api.permissions import (
    IsStaffMember,
    IsStaffOrReadOnly,
    PersonaObjectPermission,
    is_staff_super_or_admin,
)

Usuario = get_user_model()


def _openapi_unscoped(view) -> bool:
    return getattr(view, 'swagger_fake_view', False)


def _active_empresa_ids(user):
    if not user.is_authenticated:
        return []
    try:
        persona = user.persona
    except Persona.DoesNotExist:
        return []
    return list(
        PersonaEmpresa.objects.filter(persona=persona, activa=True).values_list(
            'empresa_id', flat=True
        )
    )


def _cuenta_facturacion_ids_for_user(user):
    if is_staff_super_or_admin(user):
        return None
    eids = _active_empresa_ids(user)
    if not eids:
        return []
    return list(
        Empresa.objects.filter(id__in=eids)
        .values_list('cuenta_facturacion_id', flat=True)
        .distinct()
    )


@extend_schema(
    summary='Usuario autenticado actual',
    description=(
        'Usuario del JWT. Incluye `modulos`: menú según rol(es) y plan. '
        'Superusuario: módulos fijos; con `is_admin` suma gestión tenant.'
    ),
    tags=['Autenticación'],
)
class MeUsuarioView(generics.RetrieveAPIView):
    serializer_class = serializers.MeUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@tag_read_only(TAG_USUARIOS)
class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = self.queryset.order_by('id')
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        return qs.filter(pk=self.request.user.pk)


@tag_model_viewset(TAG_USUARIOS)
class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.select_related('usuario')
    serializer_class = serializers.PersonaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [permissions.IsAuthenticated(), IsStaffMember()]
        if self.action in ('update', 'partial_update', 'retrieve'):
            return [permissions.IsAuthenticated(), PersonaObjectPermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = self.queryset.order_by('id')
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        return qs.filter(usuario=self.request.user)


@tag_model_viewset(TAG_CATALOGO)
class ModuloViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ModuloSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            modulos = Modulo.objects.filter(codigo__in=['modulo'])
        elif user.is_admin:
            modulos =  Modulo.objects.filter(activo=True)
        else:
            modulos = Modulo.objects.all()
        print(f"[ModuloViewSet] user={user} superuser={user.is_superuser} admin={getattr(user, 'is_admin', None)}", flush=True)
        for x in modulos:
            print(x.codigo)
        return modulos.order_by('codigo')


@tag_model_viewset(TAG_CATALOGO)
class RolEmpresaViewSet(viewsets.ModelViewSet):
    queryset = RolEmpresa.objects.prefetch_related('rol_modulos').order_by('codigo')
    serializer_class = serializers.RolEmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.prefetch_related('plan_modulos').order_by('orden_presentacion', 'codigo')
    serializer_class = serializers.PlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class PlanModuloViewSet(viewsets.ModelViewSet):
    queryset = PlanModulo.objects.select_related('plan', 'modulo')
    serializer_class = serializers.PlanModuloSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class EstadoSuscripcionViewSet(viewsets.ModelViewSet):
    queryset = EstadoSuscripcion.objects.all().order_by('orden', 'codigo')
    serializer_class = serializers.EstadoSuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_FACTURACION)
class CuentaFacturacionViewSet(viewsets.ModelViewSet):
    queryset = CuentaFacturacion.objects.all()
    serializer_class = serializers.CuentaFacturacionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('-creado_en')
        if _openapi_unscoped(self):
            return qs
        cf_ids = _cuenta_facturacion_ids_for_user(self.request.user)
        if cf_ids is None:
            return qs
        return qs.filter(id__in=cf_ids)


@tag_model_viewset(TAG_FACTURACION)
class SuscripcionViewSet(viewsets.ModelViewSet):
    queryset = Suscripcion.objects.select_related('cuenta_facturacion', 'plan', 'estado')
    serializer_class = serializers.SuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('-creado_en')
        if _openapi_unscoped(self):
            return qs
        cf_ids = _cuenta_facturacion_ids_for_user(self.request.user)
        if cf_ids is None:
            return qs
        return qs.filter(cuenta_facturacion_id__in=cf_ids)


@tag_model_viewset(TAG_TENANCY)
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.select_related('cuenta_facturacion')
    serializer_class = serializers.EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('nombre')
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        eids = _active_empresa_ids(self.request.user)
        return qs.filter(id__in=eids)


@tag_model_viewset(TAG_TENANCY)
class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.select_related('empresa')
    serializer_class = serializers.OrganizacionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('nombre')
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        eids = _active_empresa_ids(self.request.user)
        return qs.filter(empresa_id__in=eids)


@tag_model_viewset(TAG_TENANCY)
class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.select_related('organizacion', 'organizacion__empresa')
    serializer_class = serializers.SucursalSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('nombre')
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        eids = _active_empresa_ids(self.request.user)
        return qs.filter(organizacion__empresa_id__in=eids)


@tag_model_viewset(TAG_TENANCY)
class PersonaEmpresaViewSet(viewsets.ModelViewSet):
    queryset = PersonaEmpresa.objects.select_related('persona', 'persona__usuario', 'empresa')
    serializer_class = serializers.PersonaEmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('-ingreso_en')
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        try:
            persona = self.request.user.persona
        except Persona.DoesNotExist:
            return PersonaEmpresa.objects.none()
        return qs.filter(persona=persona)


@tag_model_viewset(TAG_TENANCY)
class RolPersonaEmpresaViewSet(viewsets.ModelViewSet):
    queryset = RolPersonaEmpresa.objects.select_related(
        'persona',
        'persona__usuario',
        'rol',
    )
    serializer_class = serializers.RolPersonaEmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset
        if _openapi_unscoped(self):
            return qs
        if is_staff_super_or_admin(self.request.user):
            return qs
        try:
            persona = self.request.user.persona
        except Persona.DoesNotExist:
            return qs.none()
        return qs.filter(persona=persona)
