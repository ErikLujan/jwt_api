from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings

def create_access_token(data: dict) -> str:
    """
    Crea un token JWT de acceso de corta duración.

    **Args**:
        data (dict): Diccionario con los datos a codificar en el token. Debe contener al menos la clave 'sub' con el email del usuario.

    **Returns**:
        str: Token JWT firmado.
    """

    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Crea un token JWT de refresco de larga duración.

    **Args:**
        data: Diccionario con los datos a codificar en el token.
            Debe contener al menos la clave 'sub' con el email del usuario.

    **Returns:**
        str: Token JWT de refresco firmado.
    """

    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """
    Decodifica un token JWT y verifica su validez.

    **Args:**
        token: Token JWT a decodificar.

    **Returns:**
        dict: Payload decodificado del token.

    **Raises:**
        JWTError: Si el token es inválido o ha expirado.
    """

    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def verify_token_type(payload: dict, expected_type: str) -> bool:
    """
    Verifica que el tipo de token en el payload coincida con el tipo esperado.

    **Args:**
        payload: Payload decodificado del token.
        expected_type: Tipo de token esperado ('access' o 'refresh').

    **Returns:**
        bool: True si el tipo coincide, False en caso contrario.
    """

    return payload.get("type") == expected_type