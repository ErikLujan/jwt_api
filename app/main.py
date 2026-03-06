from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.routers import users, auth

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    tittle="FastAPI Autenticación con JWT",
    description="REST API con autenticación JWT, roles y rate limiting para regular solicitudes.",
    version="1.0.0",
    debug=settings.APP_DEBUG,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Verifica que el servidor esté corriendo correctamente.

    **Returns:**
        dict: Mensaje indicando el estado del servidor y entorno actual.
    """

    return { 
            "status": "ok", 
            ".env": settings.APP_ENV 
        }