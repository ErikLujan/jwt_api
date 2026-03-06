FROM python:3.11-slim

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copiar archivos de dependencias primero
COPY pyproject.toml .
COPY uv.lock .

# Instalar dependencias sin el proyecto en sí
RUN uv sync --frozen --no-dev

# Copiar el resto del proyecto
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]