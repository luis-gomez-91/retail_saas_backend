from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema(
    summary='Iniciar sesión (JWT)',
    description=(
        'Intercambia **username** y **password** por **access** y **refresh**. '
        'En el resto de endpoints: `Authorization: Bearer <access>`.'
    ),
    tags=['Autenticación'],
    request=TokenObtainPairSerializer,
    examples=[
        OpenApiExample(
            'Usuario local',
            value={'username': 'admin', 'password': 'admin'},
            request_only=True,
        ),
    ],
    auth=[],
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    summary='Renovar access token',
    description=(
        'Envía el **refresh** obtenido al login para recibir un nuevo **access**. '
        'Con `ROTATE_REFRESH_TOKENS` también se devuelve un refresh nuevo.'
    ),
    tags=['Autenticación'],
    request=TokenRefreshSerializer,
    examples=[
        OpenApiExample(
            'Refresh',
            value={'refresh': '<pega_el_refresh_aquí>'},
            request_only=True,
        ),
    ],
    auth=[],
)
class DocumentedTokenRefreshView(TokenRefreshView):
    pass
