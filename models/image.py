from .base import db

class Image(db.Model):
    __tablename__ = "memories-images"

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    memorie_id = db.Column(db.Integer, db.ForeignKey("memories.id"), nullable=False, unique=True)
