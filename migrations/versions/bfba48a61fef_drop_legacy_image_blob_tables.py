"""drop legacy image blob tables

These tables were already dropped by 3342137f4525 (Migrate images to URLs),
but the app kept calling db.create_all() on every boot, which silently
recreated them (empty) because the now-removed Image/UserImage models were
still registered. This migration re-drops them defensively - IF EXISTS so
it's a no-op on any database where they're already gone - now that
db.create_all() has been removed and those models no longer exist.

Revision ID: bfba48a61fef
Revises: 3342137f4525
Create Date: 2026-08-10 20:43:18.930229

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'bfba48a61fef'
down_revision = '3342137f4525'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP TABLE IF EXISTS "memories-images"')
    op.execute('DROP TABLE IF EXISTS "user-images"')


def downgrade():
    op.create_table('user-images',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('img', postgresql.BYTEA(), autoincrement=False, nullable=False),
    sa.Column('filename', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('mimetype', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('user-images_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('user-images_pkey')),
    sa.UniqueConstraint('user_id', name=op.f('user-images_user_id_key'))
    )
    op.create_table('memories-images',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('img', postgresql.BYTEA(), autoincrement=False, nullable=False),
    sa.Column('filename', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('mimetype', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('memorie_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['memorie_id'], ['memories.id'], name=op.f('memories-images_memorie_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('memories-images_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('memories-images_pkey')),
    sa.UniqueConstraint('memorie_id', name=op.f('memories-images_memorie_id_key'))
    )
