"""FastAPI application entry point."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, contexto, conversas, estatisticas, health, perguntar
from app.api.dependencies import get_current_student
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Login e cadastro são públicos para permitir a obtenção do primeiro token JWT.
app.include_router(health.router, dependencies=[Depends(get_current_student)])
app.include_router(auth.router)
app.include_router(contexto.router)
app.include_router(perguntar.router)
app.include_router(conversas.router)
app.include_router(estatisticas.router, dependencies=[Depends(get_current_student)])
