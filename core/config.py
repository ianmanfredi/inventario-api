from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "API de Inventario Profesional"
    VERSION: str = "2.0.0"

    # Base de Datos
    DATABASE_URL: str

    # Seguridad y JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Esto le dice a Pydantic que lea el archivo .env si existe
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instanciamos las configuraciones para importarlas en el proyecto
settings = Settings()
