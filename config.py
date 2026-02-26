import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    YOUTUBE_API_KEY = os.getenv("AIzaSyDQ97saYaDsSqqBmEPtbFFaYqiiTJyTjcw")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = "development"
    # Usa la variable de entorno DATABASE_URL si existe (ej. Supabase), si no, usa SQLite local
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = "production"
    # En producción, requerimos que DATABASE_URL esté configurada
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    FLASK_ENV = "testing"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    """Return the configuration class for the given name."""

    key = name or os.getenv("FLASK_ENV", "development")
    return config_by_name.get(key, DevelopmentConfig)
