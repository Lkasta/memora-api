import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from routes.auth_routes import auth_bp
from routes.memory_routes import memory_bp
from routes.img_routes import img_bp
from routes.user_routes import user_bp
from config import Config
from models import db

def create_app():
  app = Flask(__name__)
  migrate = Migrate(app, db)
  app.config.from_object(Config)

  app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "chave_dev_super_secreta")
  app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

  jwt = JWTManager(app)
  
  app.url_map.strict_slashes = False
  
  db.init_app(app)
  migrate.init_app(app, db)

  with app.app_context():
    db.create_all()

  CORS(app, 
    supports_credentials=True,
    origins=["https://memora.lkasta.com", "http://localhost:3000"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"])

  @app.route("/")
  def home():
    return "<h1>Backend rodando!</h1>"

  app.register_blueprint(auth_bp, url_prefix="/auth")
  app.register_blueprint(memory_bp, url_prefix="/memories")
  app.register_blueprint(img_bp, url_prefix="/images")
  app.register_blueprint(user_bp, url_prefix="/user")

  return app

if __name__ == "__main__":
  app_instance = create_app()
  port = int(os.environ.get("PORT", 5000))
  debug_mode = os.environ.get("FLASK_ENV") == "development"
  app_instance.run(host="0.0.0.0", port=port, debug=debug_mode)
