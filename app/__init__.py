import os
from flask import Flask
from dotenv import load_dotenv
from pathlib import Path

# Load .env before importing config so os.getenv captures values
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

from config import get_config
from .extensions import db, migrate
from .blueprints.main import main_bp
from .blueprints.api import api_bp


def create_app(config_name: str | None = None) -> Flask:
    """Application factory so we can create isolated app instances."""

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))
    # Ensure env-based settings (like YOUTUBE_API_KEY) are picked even if config was imported earlier
    app.config["YOUTUBE_API_KEY"] = os.getenv("YOUTUBE_API_KEY")

    register_extensions(app)
    register_blueprints(app)
    register_cli(app)
    
    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models so alembic/flask-migrate can detect them
    from . import models


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)



def register_cli(app: Flask) -> None:
    @app.cli.command("ping")
    def ping() -> None:
        """Quick liveness check for the CLI."""

        print("pong")
