from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.schemas.user import UserCreate, UserResponse
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
    """
    Autentica un usuario y retorna los tokens JWT.

    **Args:**
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
    """
    Genera un nuevo access token usando un refresh token válido.

    **Args:**
        body: Refresh token JWT.

    **Returns:**
        AccessTokenResponse: Nuevo access token generado.

    **Raises:**
        HTTPException: Si el refresh token es inválido o expirado.
    """

    return await auth_service.refresh_access_token(body.refresh_token)