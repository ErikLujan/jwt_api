from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
import time

from app.db.deps import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.core.config import settings
from app.core.security import get_current_active_user, bearer_scheme
from app.service.blacklist import add_to_blacklist
from app.service import auth as auth_service

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registra un nuevo usuario en el sistema.

    **Args:**
        request: Objeto de request de FastAPI, requerido por slowapi.
        user_data: Datos del usuario a registrar (email, username, password, role_id).
        db: Sesión activa de base de datos.

    **Returns:**
        UserResponse: Datos del usuario recién creado.

    **Raises:**
        HTTPException: Si el email o username ya están en uso.
    """
    return await auth_service.register_user(user_data, db)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Autentica un usuario y retorna los tokens JWT.

    **Args:**
        request: Objeto de request de FastAPI, requerido por slowapi.
        credentials: Email y contraseña del usuario.
        db: Sesión activa de base de datos.

    **Returns:**
        TokenResponse: Access token y refresh token.

    **Raises:**
        HTTPException: Si las credenciales son inválidas o la cuenta está desactivada.
    """
    return await auth_service.login_user(credentials, db)

@router.post("/refresh", response_model=AccessTokenResponse)
@limiter.limit("7/minute")
async def refresh(request: Request, body: RefreshRequest):
    """Genera un nuevo access token usando un refresh token válido.

    **Args:**
        request: Objeto de request de FastAPI, requerido por slowapi.
        body: Refresh token JWT.

    **Returns:**
        AccessTokenResponse: Nuevo access token generado.

    **Raises:**
        HTTPException: Si el refresh token es inválido o expirado.
    """
    return await auth_service.refresh_access_token(body.refresh_token)

@router.post("/logout", status_code=200)
@limiter.limit("5/minute")
async def logout(
    request: Request,
    current_user=Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """Invalida el access token del usuario autenticado.

    **Args:**
        request: Objeto de request de FastAPI, requerido por slowapi.
        current_user: Usuario autenticado extraído del token JWT.
        credentials: Credenciales Bearer extraídas del header Authorization.

    **Returns:**
        dict: Mensaje de confirmación del logout.

    **Raises:**
        RateLimitExceeded: Si se superan los 5 requests por minuto desde la misma IP.
    """
    token = credentials.credentials
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    exp = payload.get("exp")
    ttl = exp - int(time.time())

    if ttl > 0:
        await add_to_blacklist(token, ttl)

    return {"message": "Sesión cerrada correctamente."}