from .base import db, utcnow


class MemoryImage(db.Model):
    """One row per image file a memory references - the cover plus every
    ``<img>`` embedded in the body.

    The bytes themselves live in UploadThing; what this table keeps is the URL
    and the provider's file key. The file key is the part that matters: it is
    what lets the backend actually delete the file when the memory is removed
    or the image is taken out of the text, instead of leaving it orphaned in
    storage forever.
    """

    __tablename__ = "memory_images"
    __table_args__ = (
        db.UniqueConstraint(
            "memory_id", "source", "url", name="uq_memory_images_memory_source_url"
        ),
    )

    SOURCE_COVER = "cover"
    SOURCE_CONTENT = "content"

    id = db.Column(db.Integer, primary_key=True)
    memory_id = db.Column(
        db.Integer,
        db.ForeignKey("memories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = db.Column(db.String(1000), nullable=False)
    # None for anything that isn't UploadThing-hosted (an <img> pasted from
    # elsewhere on the web, a data URI). Those are still tracked, so the row
    # count stays honest, but they are never deleted remotely.
    file_key = db.Column(db.String(255), nullable=True, index=True)
    source = db.Column(db.String(16), nullable=False, default=SOURCE_CONTENT)
    created_at = db.Column(db.DateTime, default=utcnow)

    def __repr__(self) -> str:
        return (
            f"<MemoryImage id={self.id} memory_id={self.memory_id} "
            f"source={self.source!r} file_key={self.file_key!r}>"
        )
