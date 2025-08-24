import os  # <-- Import necessário
from flask import Flask
from config import Config
from models import db
from routes.memory_routes import memory_bp

def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)

  with app.app_context():
    db.create_all()

  @app.route("/")
  def home():
    return "<h1>Backend rodando!</h1>"

  app.register_blueprint(memory_bp, url_prefix="/memories")

  return app

if __name__ == "__main__":
  app_instance = create_app()
  port = int(os.environ.get("PORT", 5000))
  app_instance.run(host="0.0.0.0", port=port, debug=True)
