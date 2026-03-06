from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Schema para la solicitud de login.

    **Args:**
        email: Correo electrónico del usuario.
        password: Contraseña en texto plano.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Schema para la respuesta de autenticación.

    **Returns:**
        access_token: Token JWT de acceso de corta duración.
        refresh_token: Token JWT de refresco de larga duración.
        token_type: Tipo de token, siempre 'bearer'.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """
    Schema para la solicitud de refresco de token.

    **Args:**
        refresh_token: Token JWT de refresco válido.
    """

    refresh_token: str


class AccessTokenResponse(BaseModel):
    """
    Schema para la respuesta con el nuevo access token.

    **Returns:**
        access_token: Nuevo token JWT de acceso.
        token_type: Tipo de token, siempre 'bearer'.
    """

    access_token: str
    token_type: str = "bearer"