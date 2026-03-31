from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# --- ESQUEMAS PARA PRODUCTOS ---


class ProductBase(BaseModel):
    """Esquema base con los campos comunes de un producto."""

    name: str = Field(..., min_length=1, max_length=100, examples=["Notebook HP"])
    description: Optional[str] = Field(None, max_length=500, examples=["Laptop 15 pulgadas"])
    price: float = Field(..., gt=0, examples=[459999.99])
    stock: int = Field(..., ge=0, examples=[25])
    min_stock: int = Field(default=5, ge=0, examples=[5])


class ProductCreate(ProductBase):
    """Esquema para crear un producto nuevo (hereda todo de ProductBase)."""

    pass


class ProductUpdate(BaseModel):
    """Esquema para actualizar un producto (campos opcionales)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """Esquema de respuesta al devolver un producto (incluye ID y timestamps)."""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
