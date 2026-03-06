from pydantic import BaseModel, EmailStr
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """
    Schema base para el usuario.
    """

    email: EmailStr
    username: str


class UserCreate(UserBase):
    """
    Schema para la creación de un usuario.

    **Args:**
        email: Correo electrónico del usuario.
        username: Nombre de usuario único.
        password: Contraseña en texto plano (se hashea antes de guardar).
        role_id: Identificador del rol asignado al usuario.
    """

    password: str
    role_id: int = 2


class UserResponse(UserBase):
    """
    Schema para la respuesta de un usuario.

    **Returns:**
        id: Identificador único del usuario.
        email: Correo electrónico del usuario.
        username: Nombre de usuario.
        is_active: Estado de la cuenta.
        role: Rol asignado al usuario.
    """

    id: int
    is_active: bool
    role: RoleResponse

    model_config = {"from_attributes": True}