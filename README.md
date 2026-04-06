# Retail SaaS Backend

API REST en **Django** con **Django REST Framework** para un producto retail multitenant: empresas, organizaciones, sucursales, planes, suscripciones, facturación y **RBAC** (módulos, permisos, roles). Autenticación con **JWT** (Simple JWT).

## Requisitos

- Python 3.12+ (el proyecto usa dependencias compatibles con Django 6)
- Opcional: **PostgreSQL** (si defines `DATABASE_URL`); por defecto se usa **SQLite**

## Configuración rápida

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz del repositorio si necesitas base de datos distinta de SQLite:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd
```

Aplica migraciones y (solo desarrollo) deja datos de ejemplo y usuario `admin` / `admin`:

```bash
python manage.py migrate
python manage.py bootstrap_dev
```

> `bootstrap_dev` solo corre con `DEBUG=True` o con `ALLOW_BOOTSTRAP=1` (no usar en producción de forma habitual).

## Servidor de desarrollo

```bash
python manage.py runserver
```

La API vive bajo el prefijo **`/api/`**.

## Documentación de la API

| Recurso        | Ruta            |
|----------------|-----------------|
| OpenAPI 3      | `/api/schema/`  |
| Swagger UI     | `/api/docs/`    |
| ReDoc          | `/api/redoc/`   |

Convenciones de permisos (resumen): la mayoría de recursos exigen usuario autenticado; las operaciones de escritura suelen requerir `is_staff`, con excepciones documentadas en el esquema OpenAPI (por ejemplo, perfil de `Person`).

Más detalle en [docs/API.md](docs/API.md) (JWT, ejemplos con `curl`, convenciones).

## Estructura relevante

- `config/` — proyecto Django (`settings`, URLs raíz).
- `core/` — aplicación principal: modelos, API (`core/api/`), admin, comandos de gestión (`bootstrap_dev`, `seed_saas_catalog`).

## Admin de Django

Panel en `/admin/` (crea superusuario con `python manage.py createsuperuser` si no usas solo `bootstrap_dev`).
