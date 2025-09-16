from __future__ import annotations

from pathlib import Path

from flask import Flask

from .config import get_settings
from .web.routes import web_bp


def create_app() -> Flask:
    settings = get_settings()
    root_dir = Path(__file__).resolve().parents[2]
    template_folder = root_dir / "templates"
    static_folder = root_dir / "static"
    app = Flask(__name__, template_folder=str(template_folder), static_folder=str(static_folder))
    app.config["SETTINGS"] = settings
    app.secret_key = settings.secret_key

    app.register_blueprint(web_bp)
    return app


app = create_app()
