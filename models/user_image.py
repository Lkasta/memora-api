from .base import db

class UserImage(db.Model):
    __tablename__ = "user-images"

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
