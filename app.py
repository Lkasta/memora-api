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

  app.register_blueprint(memory_bp, url_prefix="/memories")

  return app

if __name__ == "__main__":
  app_instance = create_app()
  app_instance.run(debug=True)
