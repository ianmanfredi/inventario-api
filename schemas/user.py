from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# --- ESQUEMAS PARA USUARIOS ---


class UserCreate(BaseModel):
    """Esquema para registrar un usuario nuevo."""

    username: str = Field(..., min_length=3, max_length=50, examples=["admin"])
    password: str = Field(..., min_length=6, examples=["miContraseñaSegura123"])


class UserResponse(BaseModel):
    """Esquema de respuesta al devolver datos de un usuario (sin contraseña)."""

    id: int
    username: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- ESQUEMAS PARA TOKENS JWT ---


class Token(BaseModel):
    """Esquema de la respuesta del endpoint de login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos internos extraídos del token JWT."""

    username: str | None = None
