from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow() -> datetime:
    """Timezone-aware replacement for the deprecated ``datetime.utcnow()``.

    Used as a column ``default`` so every timestamp in the app is generated
    the same way instead of each model rolling its own.
    """
    return datetime.now(timezone.utc)
