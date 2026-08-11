from .base import db, utcnow


class Memory(db.Model):
    __tablename__ = "memories"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

    # passive_deletes lets the database's ON DELETE CASCADE do the work, so
    # deleting a memory doesn't have to load every image row first.
    images = db.relationship(
        "MemoryImage",
        backref="memory",
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Memory id={self.id} title={self.title!r} user_id={self.user_id}>"
