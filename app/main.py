"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes import auth, estatisticas, health, perguntar
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(perguntar.router)
app.include_router(estatisticas.router)

