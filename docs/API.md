# Documentación de la API REST

Backend **Retail SaaS**: multitenant (empresas, planes, suscripciones, RBAC). Base URL de la API: **`/api/`**.

## Documentación interactiva (OpenAPI)

Con el servidor en marcha (`python manage.py runserver`):

| Recurso | Ruta |
|--------|------|
| Esquema OpenAPI 3 | `/api/schema/` |
| **Swagger UI** | `/api/docs/` |
| **ReDoc** | `/api/redoc/` |

En Swagger/ReDoc puedes probar endpoints (tras obtener un JWT) y ver modelos de petición/respuesta.

---

## Autenticación (JWT)

1. **Obtener tokens** — `POST /api/auth/token/`  
   Cuerpo JSON:

   ```json
   {
     "username": "tu_usuario",
     "password": "tu_contraseña"
   }
   ```

   Respuesta típica:

   ```json
   {
     "access": "<token_corto>",
     "refresh": "<token_largo>"
   }
   ```

2. **Llamadas posteriores** — cabecera:

   ```http
   Authorization: Bearer <access>
   ```

3. **Renovar access** — `POST /api/auth/token/refresh/` con:

   ```json
   { "refresh": "<refresh>" }
   ```

Duración por defecto (ver `SIMPLE_JWT` en `config/settings.py`): access ~1 h, refresh ~7 días, con rotación de refresh activada.

### Ejemplo con curl

```bash
BASE=http://127.0.0.1:8000
TOKENS=$(curl -s -X POST "$BASE/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')
ACCESS=$(echo "$TOKENS" | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

curl -s "$BASE/api/users/me/" -H "Authorization: Bearer $ACCESS"
```

---

## Convenciones

- **Formato**: JSON, UTF-8.
- **Paginación**: los listados usan la paginación por defecto de DRF si está configurada (actualmente no hay `PAGE_SIZE` global; las respuestas de lista devuelven el formato estándar del router).
- **Errores**: códigos HTTP habituales (`401` sin token o token inválido, `403` sin permiso, `404`, validación `400`).

---

## Permisos resumidos

| Situación | Comportamiento |
|-----------|----------------|
| Sin `Authorization` | `401` en casi todos los recursos (salvo login/refresh). |
| Usuario autenticado, **sin** `is_staff` | **GET**: datos filtrados a sus empresas (membresías activas) donde aplica; **POST/PUT/PATCH/DELETE**: en la mayoría de recursos solo **staff**. |
| Usuario con `is_staff` | Acceso completo CRUD según la vista (sin filtro de tenant en listados). |
| **`Person`** | Cada usuario puede **ver/editar** su propia persona; **crear/borrar** personas: **staff**. |
| **`UserIdentity`** | Lectura de identidades propias; **escritura**: **staff**. |
| **`User`** | Solo **lectura**; sin staff solo ve su propio usuario. |

---

## Recursos y rutas

Todos bajo `/api/` (trailing slash según `APPEND_SLASH` de Django).

### Autenticación y perfil

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/token/` | Login JWT |
| POST | `/api/auth/token/refresh/` | Renovar access |
| GET | `/api/users/me/` | Usuario actual |

### Usuarios y personas

| Recurso | Ruta base (CRUD estándar) |
|---------|---------------------------|
| Usuarios (`User`) | `/api/users/` |
| Personas (`Person`) | `/api/persons/` |
| Proveedores de auth | `/api/auth-providers/` |
| Identidades de usuario | `/api/user-identities/` |

### Catálogo y RBAC

| Recurso | Ruta base |
|---------|-----------|
| Módulos | `/api/modules/` |
| Permisos de app | `/api/app-permissions/` |
| Roles | `/api/roles/` (en escritura: `permission_ids` para el M2M) |
| Módulo por rol | `/api/module-roles/` |
| Planes | `/api/plans/` (lectura incluye `module_ids`) |
| Plan ↔ módulo | `/api/plan-modules/` |
| Estados de suscripción | `/api/subscription-statuses/` |

### Facturación

| Recurso | Ruta base |
|---------|-----------|
| Cuentas de facturación | `/api/billing-accounts/` |
| Suscripciones | `/api/subscriptions/` |

### Tenancy

| Recurso | Ruta base |
|---------|-----------|
| Empresas | `/api/empresas/` |
| Organizaciones | `/api/organizaciones/` |
| Sucursales | `/api/sucursales/` |
| Membresía persona–empresa | `/api/person-empresas/` |
| Asignación de rol con alcance | `/api/person-role-assignments/` |

### Operaciones CRUD por ViewSet

Para cada recurso anterior, el router expone habitualmente:

- `GET /api/<recurso>/` — listado  
- `POST /api/<recurso>/` — crear (si tienes permiso)  
- `GET /api/<recurso>/{id}/` — detalle  
- `PUT` / `PATCH /api/<recurso>/{id}/` — actualizar  
- `DELETE /api/<recurso>/{id}/` — borrar  

Los `id` son numéricos (BigAutoField).

---

## Exportar el esquema en archivo

```bash
python manage.py spectacular --file openapi.yaml
```

Útil para clientes (OpenAPI Generator, Postman, etc.).

---

## CORS

En desarrollo (`DEBUG=True`) está `CORS_ALLOW_ALL_ORIGINS`. En producción define orígenes explícitos en `config/settings.py`.
