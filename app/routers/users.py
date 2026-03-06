from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def get_me(request: Request, current_user: User = Depends(get_current_active_user)):
    """
    Obtiene los datos del usuario autenticado.

    **Args:**
        current_user: Usuario autenticado obtenido del token JWT.

    **Returns:**
        UserResponse: Datos del usuario autenticado.
    """

    return current_user

@router.get("/admin-only")
@limiter.limit("5/minute")
async def admin_only(request: Request, current_user: User = Depends(require_admin)):
    """
    Endpoint de prueba accesible solo para administradores.

    **Args:**
        current_user: Usuario autenticado con rol de administrador.

    **Returns:**
        dict: Mensaje de confirmación con el username del admin.
    """

    return { "message": f"Buenas tardes admin {current_user.username}, tenes acceso total a esta ruta." }