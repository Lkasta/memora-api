from sqlalchemy.orm import validates

from security.password_handler import PasswordHandler
from .base import db, utcnow


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    memories = db.relationship("Memory", backref="user", lazy=True)
    profile_image_url = db.Column(db.String(500), nullable=True)

    @validates("email")
    def normalize_email(self, _key, value):
        """Keep emails consistently lowercase/trimmed so lookups never miss
        a match just because of casing (e.g. "User@x.com" vs "user@x.com")."""
        return value.strip().lower() if value else value

    def set_password(self, password: str) -> None:
        self.password = PasswordHandler.encrypt_password(password)

    def check_password(self, password: str) -> bool:
        return PasswordHandler.check_password(password, self.password)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
