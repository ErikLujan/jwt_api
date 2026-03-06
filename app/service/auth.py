from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from jose import JWTError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, AccessTokenResponse
from app.schemas.user import UserCreate
from app.service import jwt as jwt_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashea la contraseña en texto plano utilizando bcrypt.

    **Args**:
        password (str): Contraseña en texto plano a hashear.

    **Returns**:
        str: Contraseña hasheada.
    """

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.

    **Args:**
        plain_password: Contraseña en texto plano ingresada por el usuario.
        hashed_password: Hash almacenado en la base de datos.

    **Returns:**
        bool: True si la contraseña es correcta, False en caso contrario.
    """

    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    Busca un usuario en la base de datos por su email.

    **Args:**
        email: Correo electrónico a buscar.
        db: Sesión activa de base de datos.

    **Returns:**
        User | None: El usuario encontrado o None si no existe.
    """

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.email == email)
    )
    return result.scalar_one_or_none()

async def register_user(user_data: UserCreate, db: AsyncSession) -> User:

    existing = await get_user_by_email(user_data.email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ya registrado"
        )
    
    new_user = User(
        email = user_data.email,
        username = user_data.username,
        hashed_password = hash_password(user_data.password),
        role_id = user_data.role_id
    )

    db.add(new_user)
    await db.flush()

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == new_user.id)
    )

    return result.scalar_one()

async def login_user(credentials: LoginRequest, db: AsyncSession) -> TokenResponse:
    """
    Autentica un usuario y retorna los tokens JWT.

    **Args:**
        credentials: Email y contraseña del usuario.
        db: Sesión activa de base de datos.

    **Returns:**
        TokenResponse: Access token y refresh token generados.

    **Raises:**
        HTTPException: Si las credenciales son inválidas o el usuario está inactivo.
    """

    user = await get_user_by_email(credentials.email, db)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada por inactividad."
        )
    
    payload = { "sub": user.email, "role": user.role_id }
    
    return TokenResponse(
        access_token = jwt_service.create_access_token(payload),
        refresh_token = jwt_service.create_refresh_token(payload)
    )

async def refresh_access_token(refresh_token: str) -> AccessTokenResponse:
    """
    Genera un nuevo access token a partir de un refresh token válido.

    **Args:**
        refresh_token: Token JWT de refresco.

    **Returns:**
        AccessTokenResponse: Nuevo access token generado.

    **Raises:**
        HTTPException: Si el refresh token es inválido o no es del tipo correcto.
    """

    try:
        payload = jwt_service.decode_token(refresh_token)
        if not jwt_service.verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de refresh inválido"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido o expirado"
        )
    
    new_payload = { "sub": payload["sub"], "role": payload["role"] }

    return AccessTokenResponse(
        access_token = jwt_service.create_access_token(new_payload)
    )