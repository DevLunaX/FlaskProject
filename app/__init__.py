from flask import Flask

from config import get_config
from .blueprints.main import main_bp


def create_app(config_name: str | None = None) -> Flask:
    """Application factory so we can create isolated app instances."""

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))

    register_blueprints(app)
    register_cli(app)
    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)


def register_cli(app: Flask) -> None:
    @app.cli.command("ping")
    def ping() -> None:
        """Quick liveness check for the CLI."""

        print("pong")
