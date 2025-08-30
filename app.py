import os
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.memory_routes import memory_bp

def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)
  
  app.url_map.strict_slashes = False
  
  db.init_app(app)

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

  app.register_blueprint(memory_bp, url_prefix="/memories")

  return app

if __name__ == "__main__":
  app_instance = create_app()
  port = int(os.environ.get("PORT", 5000))
  # Para produção, desabilite o debug
  debug_mode = os.environ.get("FLASK_ENV") == "development"
  app_instance.run(host="0.0.0.0", port=port, debug=debug_mode)
