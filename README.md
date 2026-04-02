# Retail API

API monolítica en [NestJS](https://nestjs.com/) con [Prisma](https://www.prisma.io/) y PostgreSQL: geografía (países y divisiones administrativas), autenticación (correo/contraseña y OAuth), usuarios, roles y permisos.

## Requisitos

- Node.js (LTS recomendado)
- PostgreSQL
- npm

## Configuración

1. Copia el ejemplo de variables de entorno:

   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y define al menos `DATABASE_URL`, `JWT_SECRET` y `PORT` si lo necesitas.

3. Para OAuth con Google o Facebook, completa las variables correspondientes en `.env`. Si no las defines, las rutas OAuth no registrarán las estrategias y solo podrás usar registro/inicio de sesión por correo.

## Instalación

```bash
npm install
```

Tras `npm install` se ejecuta `prisma generate` (script `postinstall`).

## Base de datos

Aplicar migraciones en desarrollo:

```bash
npm run prisma:migrate
```

Poblar datos iniciales (proveedores OAuth en catálogo y tipos de identificación):

```bash
npm run db:seed
```

## Scripts útiles

| Comando | Descripción |
|--------|-------------|
| `npm run start:dev` | Servidor en modo desarrollo con recarga |
| `npm run build` | Compila a `dist/` |
| `npm run start:prod` | Ejecuta `node dist/main` |
| `npm run lint` | ESLint con corrección automática |
| `npm run test` | Tests unitarios |
| `npm run prisma:generate` | Regenera el cliente Prisma |
| `npm run db:seed` | Ejecuta el seed |

## Documentación HTTP (Swagger)

Con la aplicación en marcha, la documentación interactiva está en:

`http://localhost:3000/api`

(La documentación usa autenticación Bearer JWT en los endpoints protegidos.)

## Estructura destacada

- `src/auth` — Registro, login, JWT, OAuth (Google/Facebook), perfil (`/auth/me`)
- `src/users` — Listado y actualización de usuarios y datos de persona
- `src/rbac` — Tipos de identificación, roles, permisos y asignaciones
- `src/core/geography` — Países, tipos de división y divisiones administrativas
- `prisma/schema.prisma` — Modelo de datos y migraciones en `prisma/migrations/`

## Licencia

UNLICENSED (uso privado según `package.json`).
