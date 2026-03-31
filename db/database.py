from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings

# Configuramos el motor usando la URL que viene de las variables de entorno (.env)
# El "check_same_thread" en False es un requisito específico cuando usamos SQLite con FastAPI.
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creamos la fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta es la clase base de la que van a heredar todos nuestros modelos (tablas)
Base = declarative_base()
