from app.core.redis import redis_client

async def add_to_blacklist(token: str, expires_in: int) -> None:
    """
    Agrega un token a la blacklist con TTL automático.

    **Args:**
        token: El token JWT a invalidar.
        expires_in: Segundos hasta que el token expira naturalmente.
    """
    await redis_client.setex(f"blacklist:{token}", expires_in, "true")


async def is_blacklisted(token: str) -> bool:
    """
    Verifica si un token está en la blacklist.

    **Args:**
        token: El token JWT a verificar.

    **Returns:**
        bool: True si el token está invalidado, False si es válido.
    """
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None