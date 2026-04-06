from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.api import views
from core.api.auth_views import DocumentedTokenObtainPairView, DocumentedTokenRefreshView

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('persons', views.PersonViewSet, basename='person')
router.register('auth-providers', views.AuthProviderViewSet, basename='authprovider')
router.register('user-identities', views.UserIdentityViewSet, basename='useridentity')
router.register('modules', views.ModuleViewSet, basename='module')
router.register('app-permissions', views.AppPermissionViewSet, basename='apppermission')
router.register('roles', views.RoleViewSet, basename='role')
router.register('module-roles', views.ModuleRoleViewSet, basename='modulerole')
router.register('plans', views.PlanViewSet, basename='plan')
router.register('plan-modules', views.PlanModuleViewSet, basename='planmodule')
router.register('subscription-statuses', views.SubscriptionStatusViewSet, basename='subscriptionstatus')
router.register('billing-accounts', views.BillingAccountViewSet, basename='billingaccount')
router.register('subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register('empresas', views.EmpresaViewSet, basename='empresa')
router.register('organizaciones', views.OrganizacionViewSet, basename='organizacion')
router.register('sucursales', views.SucursalViewSet, basename='sucursal')
router.register('person-empresas', views.PersonEmpresaViewSet, basename='personempresa')
router.register('person-role-assignments', views.PersonRoleAssignmentViewSet, basename='personroleassignment')

urlpatterns = [
    path('auth/token/', DocumentedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', DocumentedTokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', views.MeUserView.as_view(), name='user-me'),
    path('', include(router.urls)),
]
