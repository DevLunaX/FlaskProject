import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = "production"


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
