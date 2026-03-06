from pydantic import BaseModel


class RoleBase(BaseModel):
    """
    Schema base para el rol.
    """

    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    """
    Schema para la creación de un rol.
    """
    pass


class RoleResponse(RoleBase):
    """
    Schema para la respuesta de un rol.
    
    **Returns:**
        id: Identificador único del rol.
        name: Nombre del rol.
        description: Descripción opcional del rol.
    """

    id: int

    model_config = {"from_attributes": True}