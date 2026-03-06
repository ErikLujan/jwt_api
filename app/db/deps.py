from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia que provee una sesión de base de datos por request.

    Abre una sesión al inicio del request y la cierra automáticamente
    al finalizar, tanto en caso de éxito como de error.

    **Yields:**
        AsyncSession: Sesión activa de SQLAlchemy para interactuar con la base de datos.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise