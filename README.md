# JWT Auth API

REST API con autenticación JWT completa, sistema de roles y rate limiting. Construida con FastAPI y PostgreSQL (Supabase), pensada como base sólida para proyectos backend que requieran un sistema de autenticación production-ready.

## Stack

- **FastAPI** — framework web async
- **SQLAlchemy 2.0** — ORM con soporte async
- **Alembic** — migraciones de base de datos
- **asyncpg** — driver async para PostgreSQL
- **python-jose** — generación y validación de JWT
- **passlib + bcrypt** — hasheo de contraseñas
- **slowapi** — rate limiting por IP
- **Supabase** — PostgreSQL hosteado
- **uv** — gestión de dependencias y entorno virtual

## Estructura del proyecto

```
jwt_api/
├── app/
│   ├── core/
│   │   ├── config.py        # Configuración centralizada via .env
│   │   └── redis.py         # Cliente Redis para blacklist de tokens
│   │   └── security.py      # Dependencias de autenticación y roles
│   ├── db/
│   │   ├── base.py          # Base declarativa de SQLAlchemy
│   │   ├── deps.py          # Dependencia de sesión DB por request
│   │   └── session.py       # Engine y sessionmaker async
│   ├── models/
│   │   ├── role.py          # Modelo Role
│   │   └── user.py          # Modelo User
│   ├── routers/
│   │   ├── auth.py          # Endpoints de autenticación
│   │   └── users.py         # Endpoints de usuarios
│   ├── schemas/
│   │   ├── auth.py          # Schemas de login, tokens
│   │   └── user.py          # Schemas de usuario
│   ├── services/
│   │   ├── auth.py          # Lógica de registro, login, refresh
│   │   └── jwt.py           # Creación y validación de tokens
│   └── main.py              # Entry point, configuración de la app
├── alembic/                 # Migraciones
├── .env.example
└── pyproject.toml
```

## Instalación

### Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Una instancia de PostgreSQL (local o Supabase)

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/jwt_api.git
cd jwt_api

# Crear y activar el entorno virtual
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editá .env con tus credenciales
```

### Variables de entorno

```env
# App
APP_ENV=development
APP_DEBUG=true

# JWT
JWT_SECRET_KEY=tu-clave-secreta
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Base de datos
DATABASE_URL=postgresql+asyncpg://usuario:password@host:5432/dbname

# Redis (preparado para rate limiting distribuido)
REDIS_URL=redis://localhost:6379
```

### Base de datos

Ejecutá este SQL en tu instancia de PostgreSQL para crear las tablas:

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

INSERT INTO roles (name, description) VALUES
    ('admin', 'Administrador con acceso total'),
    ('user', 'Usuario estándar');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    role_id INTEGER NOT NULL REFERENCES roles(id)
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_username ON users(username);
```

### Levantar el servidor

```bash
uvicorn app.main:app --reload
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.

## Endpoints

### Autenticación

| Método | Endpoint | Descripción | Rate limit |
|--------|----------|-------------|------------|
| POST | `/auth/register` | Registro de usuario | 3/min |
| POST | `/auth/login` | Login, retorna tokens JWT | 5/min |
| POST | `/auth/refresh` | Refresca el access token | 7/min |

#### POST /auth/register

```json
// Request
{
  "email": "usuario@ejemplo.com",
  "username": "usuario",
  "password": "MiPassword123",
  "role_id": 2
}

// Response 201
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "usuario",
  "is_active": true,
  "role": {
    "id": 2,
    "name": "user",
    "description": "Usuario estándar"
  }
}
```

#### POST /auth/login

```json
// Request
{
  "email": "usuario@ejemplo.com",
  "password": "MiPassword123"
}

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST /auth/refresh

```json
// Request
{
  "refresh_token": "eyJ..."
}

// Response 200
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Usuarios

Los endpoints de usuarios requieren el header `Authorization: Bearer <access_token>`.

| Método | Endpoint | Descripción | Roles permitidos | Rate limit |
|--------|----------|-------------|------------------|------------|
| GET | `/users/me` | Datos del usuario autenticado | user, admin | 10/min |
| GET | `/users/admin-only` | Endpoint restringido | admin | 5/min |

## Seguridad

- Las contraseñas se hashean con **bcrypt** antes de almacenarse.
- Los tokens JWT tienen tiempo de expiración configurable. El access token tiene vida corta (30 min por defecto) y el refresh token vida larga (7 días).
- Los tokens incluyen un campo `type` para evitar que un refresh token sea usado como access token y viceversa.
- El rate limiting opera por IP y está aplicado especialmente en los endpoints de autenticación para mitigar ataques de fuerza bruta.
- Los roles se validan en cada request mediante dependencias de FastAPI, no en el token.

## Decisiones técnicas

**¿Por qué JWT con refresh tokens y no solo access tokens?**
Un access token de larga duración es un riesgo: si se filtra, el atacante tiene acceso por mucho tiempo. La combinación access + refresh permite tokens de corta vida sin forzar al usuario a re-loguearse constantemente.

**¿Por qué SQLAlchemy async en lugar del cliente de Supabase?**
El cliente de Supabase abstrae demasiado el acceso a datos. SQLAlchemy con Alembic da control total sobre el esquema, las queries y las migraciones — algo importante cuando el proyecto crece.

**¿Por qué los roles se validan en el servidor y no en el token?**
Validar roles desde el token significa que un cambio de rol no tiene efecto hasta que el token expire. Al consultar el rol desde la base de datos en cada request, el cambio es inmediato.
