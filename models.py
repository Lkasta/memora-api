from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from drivers.password_handler import PasswordHandler

db = SQLAlchemy()
password_handler = PasswordHandler()

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.LargeBinary(128), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  memories = db.relationship("Memory", backref="user", lazy=True)

  def set_password(self, password: str):
    self.password = password_handler.encrypt_password(password)

  def check_password(self, password: str) -> bool:
    return password_handler.check_password(password, self.password)

class Memory(db.Model):
  __tablename__ = "memories"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=True)
  event_date = db.Column(db.DateTime, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

class Image(db.Model):
  __tablename__ = "memories-images"

  id = db.Column(db.Integer, primary_key=True)
  img = db.Column(db.LargeBinary, nullable=False)
  filename = db.Column(db.String(120), nullable=False)
  mimetype = db.Column(db.Text, nullable=False)

  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  memorie_id = db.Column(db.Integer, db.ForeignKey("memories.id"), nullable=False, unique=True)
