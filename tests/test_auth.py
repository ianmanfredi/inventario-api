"""
Tests automatizados para los endpoints de autenticación (/auth).
"""


class TestAuth:
    """Suite de pruebas para el módulo de autenticación."""

    def test_register_user(self, client):
        """Debe poder registrar un usuario nuevo exitosamente."""
        response = client.post(
            "/auth/register",
            json={"username": "nuevo_user_auth", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "nuevo_user_auth"
        assert "id" in data
        # Verificar que la contraseña NO se devuelve en la respuesta
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_duplicate_user(self, client):
        """Debe rechazar un registro con un nombre de usuario que ya existe."""
        # Primero creamos el usuario
        client.post(
            "/auth/register",
            json={"username": "usuario_duplicado", "password": "password123"},
        )
        # Intentamos crearlo de nuevo
        response = client.post(
            "/auth/register",
            json={"username": "usuario_duplicado", "password": "password123"},
        )
        assert response.status_code == 400

    def test_login_success(self, client):
        """Debe poder iniciar sesión y devolver un token JWT."""
        # Primero creamos el usuario
        client.post(
            "/auth/register",
            json={"username": "login_user", "password": "testpassword123"},
        )
        response = client.post(
            "/auth/login",
            data={"username": "login_user", "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Debe rechazar el login con una contraseña incorrecta."""
        # Primero creamos el usuario
        client.post(
            "/auth/register",
            json={"username": "wrong_pw_user", "password": "correctpassword"},
        )
        response = client.post(
            "/auth/login",
            data={"username": "wrong_pw_user", "password": "contraseña_incorrecta"},
        )
        assert response.status_code == 401
