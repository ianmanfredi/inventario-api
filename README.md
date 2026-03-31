# 📦 API de Inventario Profesional

![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-d32f2f?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

API RESTful profesional para **gestión de inventario** construida con FastAPI, SQLAlchemy y autenticación JWT. Diseñada siguiendo principios de Clean Architecture, testing automatizado y lista para despliegue con Docker.

---

## ✨ Características

- **CRUD completo** de productos (crear, leer, actualizar, eliminar)
- **Registro de ventas** con descuento automático de stock
- **Autenticación JWT** con OAuth2 y hasheo bcrypt de contraseñas
- **Validación de datos** con Pydantic v2 (esquemas tipados con `Field`)
- **Arquitectura modular** con APIRouter y separación de responsabilidades
- **Migraciones de BD** con Alembic (versionado del esquema)
- **Testing automatizado** con pytest (15 tests)
- **Dockerizado** y listo para producción
- **Documentación interactiva** auto-generada (Swagger UI & ReDoc)

---

## 🗂️ Estructura del Proyecto

```
backend_inventario/
├── main.py                  # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias del proyecto
├── Dockerfile               # Imagen Docker de producción
├── docker-compose.yml       # Orquestación de servicios
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Archivos ignorados por Git
├── alembic.ini              # Configuración de migraciones
│
├── api/                     # Capa de controladores (HTTP)
│   ├── deps.py              #   Inyección de dependencias (get_db, get_current_user)
│   └── routers/
│       ├── auth.py          #   Endpoints de registro y login
│       └── products.py      #   Endpoints CRUD de productos
│
├── core/                    # Configuración y lógica transversal
│   ├── config.py            #   Variables de entorno (Pydantic Settings)
│   └── security.py          #   Hasheo de contraseñas y JWT
│
├── db/                      # Capa de persistencia
│   ├── database.py          #   Motor y sesión de SQLAlchemy
│   └── models.py            #   Modelos ORM (User, Product)
│
├── alembic/                 # Migraciones de base de datos
│   ├── env.py               #   Config de Alembic (conecta con settings)
│   └── versions/            #   Archivos de migración versionados
│
├── schemas/                 # Esquemas de validación (Pydantic)
│   ├── product.py           #   DTOs de productos
│   └── user.py              #   DTOs de usuarios y tokens
│
└── tests/                   # Pruebas automatizadas
    ├── conftest.py          #   Fixtures y configuración de pytest
    ├── test_auth.py         #   Tests de autenticación
    └── test_products.py     #   Tests de productos
```

---

## 🚀 Instalación y Ejecución

### Opción 1: Local (Desarrollo)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/backend_inventario.git
cd backend_inventario

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar las variables de entorno
cp .env.example .env
# Editar .env con tus valores (o dejar los defaults para desarrollo)

# 5. Crear la base de datos con Alembic
alembic upgrade head

# 6. Levantar el servidor
uvicorn main:app --reload
```

### Opción 2: Docker (Producción)

```bash
# Un solo comando y listo:
docker compose up --build
```

La API estará disponible en **http://localhost:8000**

---

## 📖 Documentación de la API

FastAPI genera documentación interactiva automáticamente:

| Herramienta | URL                              |
|-------------|----------------------------------|
| Swagger UI  | http://localhost:8000/docs        |
| ReDoc       | http://localhost:8000/redoc       |

---

## 🔐 Autenticación

La API usa **JWT (JSON Web Tokens)** para proteger los endpoints de escritura.

### Flujo de autenticación:

```
1. POST /auth/register  →  Crear cuenta (username + password)
2. POST /auth/login     →  Obtener token JWT
3. Usar el token en el header:  Authorization: Bearer <token>
```

### Endpoints protegidos (requieren token):
- `POST /productos/` — Crear producto
- `PUT /productos/{id}` — Actualizar producto
- `PUT /productos/{id}/vender` — Registrar venta
- `DELETE /productos/{id}` — Eliminar producto

### Endpoints públicos:
- `GET /productos/` — Listar productos
- `GET /productos/{id}` — Obtener producto por ID
- `GET /` — Health check

---

## 🗄️ Migraciones de Base de Datos (Alembic)

El esquema de la BD se gestiona con **Alembic**, lo que permite trackear cambios, hacer rollback y mantener un historial versionado.

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Crear una nueva migración después de modificar un modelo
alembic revision --autogenerate -m "descripción del cambio"

# Ver el estado actual de las migraciones
alembic current

# Ver el historial completo de migraciones
alembic history

# Hacer rollback de la última migración
alembic downgrade -1
```

---

## 🧪 Testing

```bash
# Correr todos los tests
pytest -v

# Correr con reporte de cobertura
pytest -v --tb=short
```

---

## 🛠️ Tech Stack

| Tecnología       | Uso                                |
|------------------|------------------------------------|
| **FastAPI**      | Framework web async de alto rendimiento |
| **SQLAlchemy**   | ORM para la base de datos          |
| **Pydantic v2**  | Validación y serialización de datos |
| **Alembic**      | Migraciones versionadas de BD      |
| **python-jose**  | Creación y verificación de JWT     |
| **bcrypt**       | Hasheo seguro de contraseñas       |
| **pytest**       | Framework de testing               |
| **Docker**       | Containerización y despliegue      |

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.
