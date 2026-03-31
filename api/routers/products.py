from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from db.models import Product, User
from schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un producto nuevo",
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un nuevo producto en el inventario.
    **Requiere autenticación (token JWT).**
    """
    db_product = db.query(Product).filter(Product.name == product.name).first()
    if db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un producto con ese nombre",
        )

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        min_stock=product.min_stock,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="Listar todos los productos",
)
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Devuelve una lista paginada de todos los productos del inventario.
    Este endpoint es público (no requiere autenticación).
    """
    return db.query(Product).offset(skip).limit(limit).all()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Obtener un producto por ID",
)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Devuelve un producto específico buscado por su ID.
    Este endpoint es público.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return db_product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Actualizar un producto",
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza los campos de un producto existente.
    Solo se actualizan los campos enviados en el body.
    **Requiere autenticación (token JWT).**
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@router.put(
    "/{product_id}/vender",
    response_model=ProductResponse,
    summary="Registrar una venta (descontar 1 unidad de stock)",
)
def sell_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Registra una venta: descuenta 1 unidad del stock del producto.
    **Requiere autenticación (token JWT).**
    Devuelve error si el stock está en 0.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    if db_product.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sin stock disponible",
        )

    db_product.stock -= 1
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un producto",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina un producto del inventario de forma permanente.
    **Requiere autenticación (token JWT).**
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    db.delete(db_product)
    db.commit()
    return {"mensaje": f"Producto '{db_product.name}' eliminado correctamente"}
