"""
Configuración compartida de pytest para las pruebas de la API.
Crea una base de datos SQLite en memoria para cada sesión de tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from api.deps import get_db
from main import app

# Base de datos en memoria para tests (aislada de la real)
SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Sobreescribimos la dependencia get_db para usar la DB de test
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea las tablas antes de correr los tests y las elimina después."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    # Limpiar archivo de test
    import os

    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture()
def client():
    """Cliente HTTP de prueba para interactuar con la API."""
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    """
    Registra un usuario de prueba, hace login y devuelve los headers
    de autorización para usar en endpoints protegidos.
    """
    import uuid

    unique_user = f"testuser_{uuid.uuid4().hex[:8]}"

    # Registrar un usuario de prueba
    client.post(
        "/auth/register",
        json={"username": unique_user, "password": "testpassword123"},
    )

    # Hacer login para obtener el token
    response = client.post(
        "/auth/login",
        data={"username": unique_user, "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
