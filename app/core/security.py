from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.models.user import User
from app.service import jwt as jwt_service
from app.service.auth import get_user_by_email
from app.service.blacklist import is_blacklisted

bearer_scheme = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db)
    ) -> User:
    """
    Dependencia que obtiene el usuario autenticado a partir del access token.

    Extrae y valida el token JWT del header Authorization,
    luego busca y retorna el usuario correspondiente.

    **Args:**
        credentials: Credenciales HTTP Bearer extraídas del header.
        db: Sesión activa de base de datos.

    **Returns:**
        User: El usuario autenticado.

    **Raises:**
        HTTPException: Si el token es inválido, expirado, o el usuario no existe.
    """
    token = credentials.credentials

    if await is_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token invalidado.")

    try:
        payload = jwt_service.decode_token(credentials.credentials)
        if not jwt_service.verify_token_type(payload, "access"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido"
            )
        
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado"
        )
    
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia que verifica que el usuario autenticado esté activo.

    **Args:**
        current_user: Usuario obtenido desde get_current_user.

    **Returns:**
        User: El usuario autenticado y activo.

    **Raises:**
        HTTPException: Si la cuenta del usuario está desactivada.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada por inactividad."
        )
    
    return current_user

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependencia que restringe el acceso solo a usuarios con rol de administrador.

    **Args:**
        current_user: Usuario autenticado y activo.

    **Returns:**
        User: El usuario autenticado con rol admin.

    **Raises:**
        HTTPException: Si el usuario no tiene el rol de administrador.
    """

    if current_user.role_id != 1: # El 1 es el equivalente a admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso permitido solo a administradores."
        )
    
    return current_user