from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.routers import auth, users

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="JWT Auth API",
    description="API REST con autenticacion JWT, roles y rate limiting",
    version="0.1.0",
    debug=settings.APP_DEBUG,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Rate Limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(users.router)

# ── Security Headers ─────────────────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response

@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica que el servidor esté corriendo correctamente.

    **Returns:**
        dict: Estado del servidor y entorno actual.
    """
    return {"status": "ok", "env": settings.APP_ENV}