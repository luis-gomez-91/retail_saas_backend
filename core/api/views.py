from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, viewsets

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

from core.api import serializers
from core.api.openapi import (
    TAG_CATALOGO,
    TAG_FACTURACION,
    TAG_TENANCY,
    TAG_USUARIOS,
    tag_model_viewset,
    tag_read_only,
)
from core.api.permissions import IsStaffMember, IsStaffOrReadOnly, PersonObjectPermission

User = get_user_model()


def _openapi_unscoped(view) -> bool:
    return getattr(view, 'swagger_fake_view', False)


def _active_empresa_ids(user):
    if not user.is_authenticated:
        return []
    try:
        person = user.person
    except Person.DoesNotExist:
        return []
    return list(
        PersonEmpresa.objects.filter(person=person, is_active=True).values_list(
            'empresa_id', flat=True
        )
    )


def _billing_account_ids_for_user(user):
    if user.is_staff:
        return None
    eids = _active_empresa_ids(user)
    if not eids:
        return []
    return list(
        Empresa.objects.filter(id__in=eids)
        .values_list('billing_account_id', flat=True)
        .distinct()
    )


@extend_schema(
    summary='Usuario autenticado actual',
    description='Devuelve el registro del usuario asociado al JWT (sin contraseña).',
    tags=['Autenticación'],
)
class MeUserView(generics.RetrieveAPIView):
    serializer_class = serializers.MeUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@tag_read_only(TAG_USUARIOS)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = self.queryset.order_by('id')
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        return qs.filter(pk=self.request.user.pk)


@tag_model_viewset(TAG_USUARIOS)
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.select_related('user')
    serializer_class = serializers.PersonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [permissions.IsAuthenticated(), IsStaffMember()]
        if self.action in ('update', 'partial_update', 'retrieve'):
            return [permissions.IsAuthenticated(), PersonObjectPermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = self.queryset.order_by('id')
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


@tag_model_viewset(TAG_USUARIOS)
class AuthProviderViewSet(viewsets.ModelViewSet):
    queryset = AuthProvider.objects.all().order_by('sort_order', 'code')
    serializer_class = serializers.AuthProviderSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_USUARIOS)
class UserIdentityViewSet(viewsets.ModelViewSet):
    queryset = UserIdentity.objects.select_related('user', 'provider')
    serializer_class = serializers.UserIdentitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsStaffMember()]

    def get_queryset(self):
        qs = self.queryset.order_by(
            '-is_primary', 'provider__sort_order', 'provider__code'
        )
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


@tag_model_viewset(TAG_CATALOGO)
class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all().order_by('code')
    serializer_class = serializers.ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class AppPermissionViewSet(viewsets.ModelViewSet):
    queryset = AppPermission.objects.select_related('module').order_by('code')
    serializer_class = serializers.AppPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('permissions').order_by('code')
    serializer_class = serializers.RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class ModuleRoleViewSet(viewsets.ModelViewSet):
    queryset = ModuleRole.objects.select_related('role', 'module')
    serializer_class = serializers.ModuleRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.prefetch_related('modules').order_by('display_order', 'code')
    serializer_class = serializers.PlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class PlanModuleViewSet(viewsets.ModelViewSet):
    queryset = PlanModule.objects.select_related('plan', 'module')
    serializer_class = serializers.PlanModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_CATALOGO)
class SubscriptionStatusViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionStatus.objects.all().order_by('sort_order', 'code')
    serializer_class = serializers.SubscriptionStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]


@tag_model_viewset(TAG_FACTURACION)
class BillingAccountViewSet(viewsets.ModelViewSet):
    queryset = BillingAccount.objects.all()
    serializer_class = serializers.BillingAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('-created_at')
        if _openapi_unscoped(self):
            return qs
        ba_ids = _billing_account_ids_for_user(self.request.user)
        if ba_ids is None:
            return qs
        return qs.filter(id__in=ba_ids)


@tag_model_viewset(TAG_FACTURACION)
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.select_related('billing_account', 'plan', 'status')
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('-created_at')
        if _openapi_unscoped(self):
            return qs
        ba_ids = _billing_account_ids_for_user(self.request.user)
        if ba_ids is None:
            return qs
        return qs.filter(billing_account_id__in=ba_ids)


@tag_model_viewset(TAG_TENANCY)
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.select_related('billing_account')
    serializer_class = serializers.EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('name')
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        eids = _active_empresa_ids(self.request.user)
        return qs.filter(id__in=eids)


@tag_model_viewset(TAG_TENANCY)
class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.select_related('empresa')
    serializer_class = serializers.OrganizacionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('name')
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        eids = _active_empresa_ids(self.request.user)
        return qs.filter(empresa_id__in=eids)


@tag_model_viewset(TAG_TENANCY)
class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.select_related('organizacion', 'organizacion__empresa')
    serializer_class = serializers.SucursalSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('name')
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        eids = _active_empresa_ids(self.request.user)
        return qs.filter(organizacion__empresa_id__in=eids)


@tag_model_viewset(TAG_TENANCY)
class PersonEmpresaViewSet(viewsets.ModelViewSet):
    queryset = PersonEmpresa.objects.select_related('person', 'person__user', 'empresa')
    serializer_class = serializers.PersonEmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset.order_by('-joined_at')
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        try:
            person = self.request.user.person
        except Person.DoesNotExist:
            return PersonEmpresa.objects.none()
        return qs.filter(person=person)


@tag_model_viewset(TAG_TENANCY)
class PersonRoleAssignmentViewSet(viewsets.ModelViewSet):
    queryset = PersonRoleAssignment.objects.select_related(
        'person',
        'person__user',
        'role',
        'empresa',
        'organizacion',
        'sucursal',
    )
    serializer_class = serializers.PersonRoleAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = self.queryset
        if _openapi_unscoped(self):
            return qs
        if self.request.user.is_staff:
            return qs
        try:
            person = self.request.user.person
        except Person.DoesNotExist:
            return qs.none()
        return qs.filter(person=person)
