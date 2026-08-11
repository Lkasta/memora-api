"""track memory images

Adds ``memory_images``: one row per image file a memory references, covering
both the cover (``memories.image_url``) and every ``<img>`` embedded in the
body HTML. Tracking the provider's file key is what makes it possible to
delete the file for real when the memory goes away or the image is taken out
of the text.

The backfill scans existing memories so images uploaded before this table
existed are cleaned up like any other. The parsing here is deliberately
self-contained (a regex rather than an import from ``services``) so this
migration keeps producing the same result no matter how the app evolves.

Revision ID: c4a1f7e28d55
Revises: bfba48a61fef
Create Date: 2026-08-10 21:30:00.000000

"""
import re
from urllib.parse import urlparse

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c4a1f7e28d55'
down_revision = 'bfba48a61fef'
branch_labels = None
depends_on = None


IMG_SRC_RE = re.compile(
    r"""<img\b[^>]*?\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)')""",
    re.IGNORECASE | re.DOTALL,
)


def _extract_file_key(url):
    """UploadThing file URLs end in ``/f/<key>``; anything else has no key."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https"):
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[-2] == "f":
        return parts[-1]
    return None


def _content_image_urls(content):
    if not content:
        return []
    seen = set()
    urls = []
    for double_quoted, single_quoted in IMG_SRC_RE.findall(content):
        url = (double_quoted or single_quoted).strip()
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def upgrade():
    op.create_table(
        'memory_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('file_key', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=16), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'memory_id', 'source', 'url', name='uq_memory_images_memory_source_url'
        ),
    )
    op.create_index(
        op.f('ix_memory_images_memory_id'), 'memory_images', ['memory_id'], unique=False
    )
    op.create_index(
        op.f('ix_memory_images_file_key'), 'memory_images', ['file_key'], unique=False
    )

    _backfill()


def _backfill():
    connection = op.get_bind()
    memories = connection.execute(
        sa.text("SELECT id, content, image_url FROM memories")
    ).fetchall()

    rows = []
    for memory_id, content, image_url in memories:
        seen = set()
        if image_url:
            seen.add(("cover", image_url))
            rows.append({
                "memory_id": memory_id,
                "url": image_url,
                "file_key": _extract_file_key(image_url),
                "source": "cover",
            })
        for url in _content_image_urls(content):
            if ("content", url) in seen:
                continue
            seen.add(("content", url))
            rows.append({
                "memory_id": memory_id,
                "url": url,
                "file_key": _extract_file_key(url),
                "source": "content",
            })

    if not rows:
        return

    connection.execute(
        sa.text(
            "INSERT INTO memory_images (memory_id, url, file_key, source, created_at) "
            "VALUES (:memory_id, :url, :file_key, :source, NOW())"
        ),
        rows,
    )


def downgrade():
    op.drop_index(op.f('ix_memory_images_file_key'), table_name='memory_images')
    op.drop_index(op.f('ix_memory_images_memory_id'), table_name='memory_images')
    op.drop_table('memory_images')
