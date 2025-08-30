from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  memories = db.relationship("Memory", backref="user", lazy=True)

class Memory(db.Model):
  __tablename__ = "memories"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=True)
  event_date = db.Column(db.DateTime, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
