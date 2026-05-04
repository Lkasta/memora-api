from datetime import datetime
from drivers.password_handler import PasswordHandler
from .base import db

password_handler = PasswordHandler()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    memories = db.relationship("Memory", backref="user", lazy=True)

    image = db.relationship(
        "UserImage",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str):
        self.password = password_handler.encrypt_password(password)

    def check_password(self, password: str) -> bool:
        return password_handler.check_password(password, self.password)
