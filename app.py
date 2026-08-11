import logging
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.memory_routes import memory_bp
from routes.user_routes import user_bp

migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.validate()

    # JWT_SECRET_KEY comes from Config.from_object above; only the expiry
    # needs converting from the plain "hours" env setting to a timedelta.
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS)

    logging.basicConfig(level=logging.DEBUG if Config.DEBUG else logging.INFO)

    app.url_map.strict_slashes = False

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(
        app,
        supports_credentials=True,
        origins=Config.CORS_ORIGINS,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    register_error_handlers(app)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(memory_bp, url_prefix="/memories")
    app.register_blueprint(user_bp, url_prefix="/user")

    return app


def register_error_handlers(app):
    """Make sure every error response is JSON, never Werkzeug's default HTML
    error page - this is an API-only backend."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.description}), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception("Unhandled exception")
        db.session.rollback()
        return jsonify({"error": "Erro interno do servidor"}), 500


if __name__ == "__main__":
    app_instance = create_app()
    app_instance.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
