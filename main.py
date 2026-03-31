from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import settings
from db.database import Base, engine  # noqa: F401
from db import models  # noqa: F401 - Importar para que Alembic detecte los modelos
from api.routers import auth, products

# Las tablas se crean y actualizan mediante migraciones con Alembic:
#   alembic revision --autogenerate -m "descripción del cambio"
#   alembic upgrade head
#
# Para desarrollo rápido sin Alembic, descomentar la siguiente línea:
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API RESTful profesional para gestión de inventario con autenticación JWT, "
        "control de stock y arquitectura modular."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registrar Routers ---
app.include_router(auth.router)
app.include_router(products.router)

# --- Archivos Estáticos (CSS, JS) ---
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/health", tags=["Health Check"])
def health_check():
    """Endpoint de verificación de salud de la API."""
    return {
        "status": "ok",
        "proyecto": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/", tags=["Frontend"], include_in_schema=False)
def serve_frontend():
    """Sirve el dashboard del frontend."""
    return FileResponse(BASE_DIR / "static" / "index.html")

