from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.api import views
from core.api.auth_views import DocumentedTokenObtainPairView, DocumentedTokenRefreshView

router = DefaultRouter()
router.register('users', views.UsuarioViewSet, basename='usuario')
router.register('persons', views.PersonaViewSet, basename='persona')
router.register('modules', views.ModuloViewSet, basename='modulo')
router.register('roles', views.RolEmpresaViewSet, basename='rolempresa')
router.register('plans', views.PlanViewSet, basename='plan')
router.register('plan-modules', views.PlanModuloViewSet, basename='planmodulo')
router.register('subscription-statuses', views.EstadoSuscripcionViewSet, basename='estadosuscripcion')
router.register('billing-accounts', views.CuentaFacturacionViewSet, basename='cuentafacturacion')
router.register('subscriptions', views.SuscripcionViewSet, basename='suscripcion')
router.register('empresas', views.EmpresaViewSet, basename='empresa')
router.register('organizaciones', views.OrganizacionViewSet, basename='organizacion')
router.register('sucursales', views.SucursalViewSet, basename='sucursal')
router.register('person-empresas', views.PersonaEmpresaViewSet, basename='personaempresa')
router.register(
    'person-role-assignments',
    views.RolPersonaEmpresaViewSet,
    basename='personroleassignment',
)

urlpatterns = [
    path('auth/token/', DocumentedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', DocumentedTokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', views.MeUsuarioView.as_view(), name='user-me'),
    path('', include(router.urls)),
]
