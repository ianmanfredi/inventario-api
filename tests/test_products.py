"""
Tests automatizados para los endpoints de productos (/productos).
"""
import uuid


def _unique_name():
    return f"Producto_{uuid.uuid4().hex[:8]}"


class TestProducts:
    """Suite de pruebas para el módulo de productos."""

    def test_create_product_authenticated(self, client, auth_headers):
        """Debe poder crear un producto con un token válido."""
        name = _unique_name()
        response = client.post(
            "/productos/",
            json={
                "name": name,
                "description": "Laptop 15 pulgadas",
                "price": 459999.99,
                "stock": 25,
                "min_stock": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["stock"] == 25
        assert "id" in data

    def test_create_product_unauthenticated(self, client):
        """Debe rechazar la creación de un producto sin token JWT."""
        response = client.post(
            "/productos/",
            json={
                "name": _unique_name(),
                "description": "Mouse inalámbrico",
                "price": 25000.00,
                "stock": 100,
            },
        )
        assert response.status_code == 401

    def test_create_duplicate_product(self, client, auth_headers):
        """Debe rechazar un producto con nombre duplicado."""
        name = _unique_name()
        # Crear el producto
        client.post(
            "/productos/",
            json={"name": name, "description": "Original", "price": 100.0, "stock": 1},
            headers=auth_headers,
        )
        # Intentar crear duplicado
        response = client.post(
            "/productos/",
            json={"name": name, "description": "Duplicado", "price": 100.0, "stock": 1},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_list_products(self, client, auth_headers):
        """Debe listar productos sin requerir autenticación."""
        # Crear al menos un producto
        client.post(
            "/productos/",
            json={"name": _unique_name(), "description": "Test", "price": 10.0, "stock": 5},
            headers=auth_headers,
        )
        response = client.get("/productos/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_product_by_id(self, client, auth_headers):
        """Debe poder obtener un producto por su ID."""
        # Crear un producto y obtener su ID
        create_resp = client.post(
            "/productos/",
            json={"name": _unique_name(), "description": "Test", "price": 10.0, "stock": 5},
            headers=auth_headers,
        )
        product_id = create_resp.json()["id"]

        response = client.get(f"/productos/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id

    def test_get_product_not_found(self, client):
        """Debe devolver 404 para un ID que no existe."""
        response = client.get("/productos/9999")
        assert response.status_code == 404

    def test_update_product(self, client, auth_headers):
        """Debe poder actualizar campos parciales de un producto."""
        # Crear un producto
        name = _unique_name()
        create_resp = client.post(
            "/productos/",
            json={"name": name, "description": "Test", "price": 100.0, "stock": 10},
            headers=auth_headers,
        )
        product_id = create_resp.json()["id"]

        response = client.put(
            f"/productos/{product_id}",
            json={"price": 500000.00},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 500000.00
        assert data["name"] == name  # No se modificó

    def test_sell_product(self, client, auth_headers):
        """Debe descontar 1 unidad del stock al vender."""
        # Crear un producto con stock conocido
        create_resp = client.post(
            "/productos/",
            json={"name": _unique_name(), "description": "Test", "price": 10.0, "stock": 10},
            headers=auth_headers,
        )
        product_id = create_resp.json()["id"]

        response = client.put(f"/productos/{product_id}/vender", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 9  # Descontó 1

    def test_sell_product_unauthenticated(self, client, auth_headers):
        """Debe rechazar una venta sin token JWT."""
        # Crear un producto para intentar venderlo
        create_resp = client.post(
            "/productos/",
            json={"name": _unique_name(), "description": "Test", "price": 10.0, "stock": 5},
            headers=auth_headers,
        )
        product_id = create_resp.json()["id"]
        response = client.put(f"/productos/{product_id}/vender")
        assert response.status_code == 401

    def test_delete_product(self, client, auth_headers):
        """Debe poder eliminar un producto con autenticación."""
        # Crear un producto para eliminar
        create_resp = client.post(
            "/productos/",
            json={"name": _unique_name(), "description": "Temporal", "price": 1.00, "stock": 1},
            headers=auth_headers,
        )
        product_id = create_resp.json()["id"]

        response = client.delete(f"/productos/{product_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verificar que fue eliminado
        response = client.get(f"/productos/{product_id}")
        assert response.status_code == 404

    def test_delete_product_unauthenticated(self, client, auth_headers):
        """Debe rechazar la eliminación sin token JWT."""
        # Crear un producto
        create_resp = client.post(
            "/productos/",
            json={"name": _unique_name(), "description": "Test", "price": 10.0, "stock": 5},
            headers=auth_headers,
        )
        product_id = create_resp.json()["id"]
        response = client.delete(f"/productos/{product_id}")
        assert response.status_code == 401
