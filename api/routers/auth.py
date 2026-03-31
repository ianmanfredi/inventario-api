from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.deps import get_db
from db.models import User
from schemas.user import UserCreate, UserResponse, Token
from core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario nuevo",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un usuario nuevo en el sistema.
    - Verifica que el nombre de usuario no esté en uso.
    - Hashea la contraseña antes de guardarla (nunca se almacena en texto plano).
    """
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado",
        )

    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión y obtener un token JWT",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Autentica al usuario y devuelve un token JWT.
    - Recibe las credenciales como form-data (estándar OAuth2).
    - Si las credenciales son correctas, genera un token de acceso.
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)
